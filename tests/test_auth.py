import unittest

from thulla.auth.security import hash_secret, make_token, verify_secret, verify_token
from thulla.auth.service import AuthError, AuthService, SECURITY_QUESTIONS

Q = SECURITY_QUESTIONS[0]


class Clock:
    def __init__(self): self.t = 1_000_000.0
    def __call__(self): return self.t


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.clk = Clock()
        self.a = AuthService(":memory:", clock=self.clk)
        self.uid = self.a.register("bilal_99", "Bilu", "Sup3rSecret!", "Sup3rSecret!", Q, "Government School", "government  school")

    def test_hash_not_plaintext_and_verifies(self):
        h = hash_secret("hello123")
        self.assertNotIn("hello123", h)
        self.assertTrue(verify_secret("hello123", h))
        self.assertFalse(verify_secret("nope", h))

    def test_register_validation(self):
        with self.assertRaises(AuthError): self.a.register("bilal_99", "x", "Sup3rSecret!", "Sup3rSecret!", Q, "abc", "abc")  # dup
        with self.assertRaises(AuthError): self.a.register("new_user", "x", "Sup3rSecret!", "different!!", Q, "abc", "abc")
        with self.assertRaises(AuthError): self.a.register("new_user", "x", "short", "short", Q, "abc", "abc")
        with self.assertRaises(AuthError): self.a.register("new_user", "x", "Sup3rSecret!", "Sup3rSecret!", Q, "abc", "abd")
        with self.assertRaises(AuthError): self.a.register("bad name!", "x", "Sup3rSecret!", "Sup3rSecret!", Q, "abc", "abc")

    def test_secrets_stored_hashed(self):
        with self.a._db() as c:
            r = c.execute("SELECT * FROM users").fetchone()
            blob = " ".join(str(v) for v in dict(r).values())
        self.assertNotIn("Sup3rSecret!", blob)
        self.assertNotIn("government school", blob.lower().replace(Q.lower(), ""))

    def test_login_ok_and_generic_errors(self):
        self.assertEqual(self.a.login("BILAL_99", "Sup3rSecret!")["nickname"], "Bilu")
        for u, p in (("bilal_99", "wrong"), ("nobody", "wrong")):
            with self.assertRaises(AuthError) as cm: self.a.login(u, p)
            self.assertEqual(str(cm.exception), "Invalid username or password.")

    def test_nickname_is_not_identity(self):
        with self.assertRaises(AuthError): self.a.login("Bilu", "Sup3rSecret!")

    def test_login_lockout_and_expiry(self):
        for _ in range(5):
            with self.assertRaises(AuthError): self.a.login("bilal_99", "bad")
        with self.assertRaises(AuthError) as cm: self.a.login("bilal_99", "Sup3rSecret!")
        self.assertIn("Too many", str(cm.exception))
        self.clk.t += 6 * 60
        self.assertTrue(self.a.login("bilal_99", "Sup3rSecret!"))

    def test_recovery_flow(self):
        self.assertEqual(self.a.start_recovery("bilal_99"), Q)
        token = self.a.verify_recovery("bilal_99", " GOVERNMENT school ")
        self.a.reset_password(token, "BrandNewPass1", "BrandNewPass1")
        with self.assertRaises(AuthError): self.a.reset_password(token, "AnotherPass22", "AnotherPass22")  # reused
        with self.assertRaises(AuthError): self.a.login("bilal_99", "Sup3rSecret!")
        self.assertTrue(self.a.login("bilal_99", "BrandNewPass1"))

    def test_recovery_wrong_answer_generic_and_limited(self):
        for _ in range(5):
            with self.assertRaises(AuthError) as cm: self.a.verify_recovery("bilal_99", "wrong")
            self.assertEqual(str(cm.exception), "Recovery failed. Check your details and try again.")
        with self.assertRaises(AuthError) as cm: self.a.verify_recovery("bilal_99", "Government School")
        self.assertIn("Too many", str(cm.exception))

    def test_unknown_user_gets_stable_decoy_question(self):
        q1, q2 = self.a.start_recovery("ghost"), self.a.start_recovery("ghost")
        self.assertEqual(q1, q2); self.assertIn(q1, SECURITY_QUESTIONS)
        with self.assertRaises(AuthError) as cm: self.a.verify_recovery("ghost", "anything")
        self.assertEqual(str(cm.exception), "Recovery failed. Check your details and try again.")

    def test_reset_token_expires(self):
        token = self.a.verify_recovery("bilal_99", "government school")
        self.clk.t += 11 * 60
        with self.assertRaises(AuthError): self.a.reset_password(token, "BrandNewPass1", "BrandNewPass1")

    def test_signed_token(self):
        key = b"k" * 32
        t = make_token(7, key=key)
        self.assertEqual(verify_token(t, key=key), 7)
        self.assertIsNone(verify_token(t + "x", key=key))
        self.assertIsNone(verify_token(t, key=b"o" * 32))
        self.assertIsNone(verify_token(make_token(7, ttl=-1, key=key), key=key))

    def test_stats(self):
        self.a.record_result(self.uid, won=False, was_thulla=True)
        self.assertEqual(self.a.get_stats(self.uid), {"games_played": 1, "wins": 0, "thulla_count": 1})


if __name__ == "__main__":
    unittest.main()
