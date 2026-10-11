CSS = """
<style>
.block-container {padding-top: 1.2rem; max-width: 980px;}
.seat {border-radius: 14px; padding: .5rem .7rem; margin-bottom: .4rem;
       background: rgba(127,127,127,.12); text-align: center; font-size: .95rem;}
.seat.turn {outline: 3px solid #f5a623; background: rgba(245,166,35,.18);}
.seat.out {opacity: .5;}
.table {border-radius: 18px; padding: .8rem; margin: .5rem 0 1rem;
        background: radial-gradient(circle at 50% 40%, #1f7a4d, #145c39); color: #fff;
        text-align: center; min-height: 90px;}
.pcard {display:inline-block; background:#fff; color:#111; border-radius:8px;
        padding:.35rem .55rem; margin:.15rem; font-weight:700; font-size:1.15rem;
        box-shadow: 0 2px 6px rgba(0,0,0,.35);}
.pcard.red {color:#c62828;}
.pop {text-align:center; font-size:1.6rem; font-weight:800; padding:.6rem;
      border-radius:14px; background:rgba(245,166,35,.2); animation: pop .9s ease-out;}
@keyframes pop {0%{transform:scale(.4) rotate(-6deg);opacity:0}
                60%{transform:scale(1.15) rotate(3deg);opacity:1}
                100%{transform:scale(1) rotate(0)}}
@media (max-width: 640px) {
  .pcard {font-size: 1rem; padding:.25rem .4rem;}
  .block-container {padding-left:.6rem; padding-right:.6rem;}
}
</style>
"""
