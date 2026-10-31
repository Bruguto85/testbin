"""
Alavancagem financeira com consórcio — vídeo explicativo no estilo 3Blue1Brown.

Renderização (Manim Community, sem LaTeX):
    manim -r 1920,1080 --frame_rate 30 alavancagem_consorcio.py AlavancagemConsorcio

As legendas do roteiro são exibidas na parte inferior do vídeo e, ao final da
renderização, também são exportadas para:
    alavancagem_consorcio.srt   (legendas com tempos, prontas para a narração)
    roteiro.md                  (roteiro completo, separado por seções)

Todos os valores são ilustrativos e simplificados (sem correção monetária,
seguros ou impostos). Conteúdo educativo — não é recomendação de investimento.
"""

from pathlib import Path
import random
import textwrap

import numpy as np
from manim import *

# ---------------------------------------------------------------------------
# Estilo
# ---------------------------------------------------------------------------
FONT = "CMU Serif"
config.background_color = "#0c0d12"

C_CAP = BLUE_C      # capital próprio
C_ASSET = YELLOW    # ativo / carta de crédito
C_COST = RED_C      # custo / juros / parcela
C_GOOD = GREEN_C    # renda / ganho
C_MUTED = GREY_B

OUT_DIR = Path(__file__).resolve().parent


def T(s, size=36, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def brl(x, dec=0):
    s = f"{x:,.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def pct(x, dec=1, sign=True):
    s = f"{x:+.{dec}f}%" if sign else f"{x:.{dec}f}%"
    return s.replace(".", ",")


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ---------------------------------------------------------------------------
# Números do exemplo
# ---------------------------------------------------------------------------
CARTA = 300_000
PRAZO = 180                 # meses
TAXA_ADM = 0.18
FUNDO_RES = 0.02
TOTAL = CARTA * (1 + TAXA_ADM + FUNDO_RES)      # 360.000
PARCELA = TOTAL / PRAZO                         # 2.000

JUROS_AA = 0.11
I_M = (1 + JUROS_AA) ** (1 / 12) - 1
JUROS_SAC = I_M * CARTA * (PRAZO + 1) / 2       # ~237 mil

LANCE = 0.25 * CARTA                            # 75.000
MES_CONTEMPLA = 3
SALDO = TOTAL - MES_CONTEMPLA * PARCELA - LANCE  # 279.000
NOVA_PARCELA = SALDO / (PRAZO - MES_CONTEMPLA)  # ~1.576

ALUGUEL = 0.005 * CARTA                         # 1.500
GAP = NOVA_PARCELA - ALUGUEL                    # ~76
CAPITAL = LANCE + MES_CONTEMPLA * PARCELA       # 81.000
LEV = CARTA / CAPITAL                           # ~3,7
ALUGUEL_VAC = ALUGUEL * 10 / 12                 # 1.250
GAP_VAC = NOVA_PARCELA - ALUGUEL_VAC            # ~326


class AlavancagemConsorcio(Scene):
    # ------------------------------------------------------------------
    # Infraestrutura de legendas
    # ------------------------------------------------------------------
    def setup(self):
        self.cap = None
        self.cap_text = ""
        self.cap_start = 0.0
        self.cap_need = 0.0
        self.entries = []
        self.section_name = ""

    def section(self, name):
        self.section_name = name

    def say(self, text):
        """Troca a legenda atual. Garante tempo mínimo de leitura da anterior."""
        self.end_caption()
        wrapped = "\n".join(textwrap.wrap(text, 62))
        txt = T(wrapped, size=26, line_spacing=0.9)
        bg = BackgroundRectangle(txt, color=BLACK, fill_opacity=0.7, buff=0.14)
        cap = VGroup(bg, txt).to_edge(DOWN, buff=0.28)
        self.add_foreground_mobject(cap)
        self.cap = cap
        self.cap_text = text
        self.cap_start = self.time
        self.cap_need = max(2.6, 0.068 * len(text) + 0.6)

    def end_caption(self):
        if self.cap is None:
            return
        elapsed = self.time - self.cap_start
        if elapsed < self.cap_need:
            self.wait(self.cap_need - elapsed)
        self.entries.append((self.cap_start, self.time, self.cap_text, self.section_name))
        self.remove_foreground_mobject(self.cap)
        self.remove(self.cap)
        self.cap = None

    def clear_stage(self, run_time=0.7):
        # mantém o visual na tela enquanto a legenda atual ainda está sendo lida
        if self.cap is not None:
            remaining = self.cap_need - (self.time - self.cap_start)
            if remaining > 0:
                self.wait(remaining)
        mobs = [m for m in self.mobjects if m is not self.cap]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def write_outputs(self):
        srt = []
        for i, (a, b, text, _) in enumerate(self.entries, 1):
            srt.append(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n")
        (OUT_DIR / "alavancagem_consorcio.srt").write_text("\n".join(srt), encoding="utf-8")

        md = [
            "# Roteiro — Alavancagem financeira com consórcio",
            "",
            "Legendas exibidas no vídeo (sem narração). Tempos no formato mm:ss.",
            "",
        ]
        current = None
        for a, b, text, sec in self.entries:
            if sec != current:
                md += ["", f"## {sec}", ""]
                current = sec
            mm, ss = divmod(int(a), 60)
            md.append(f"- **[{mm:02d}:{ss:02d}]** {text}")
        md += [
            "",
            "---",
            "",
            "*Valores ilustrativos e simplificados (sem correção monetária, seguros ou",
            "impostos). Conteúdo educativo — não é recomendação de investimento.*",
            "",
        ]
        (OUT_DIR / "roteiro.md").write_text("\n".join(md), encoding="utf-8")

    # ------------------------------------------------------------------
    # Elementos reutilizáveis
    # ------------------------------------------------------------------
    def make_lever(self, big_text, small_text, big_sub=None, small_sub=None):
        pivot = np.array([-1.5, -0.9, 0])
        fulcrum = Triangle(color=GREY_B, fill_color=GREY_D, fill_opacity=1, stroke_width=2)
        fulcrum.scale(0.5).move_to(pivot, aligned_edge=UP)
        fulcrum.shift((pivot[0] - fulcrum.get_top()[0]) * RIGHT)
        ground = Line(LEFT * 6, RIGHT * 6, color=GREY_D).next_to(fulcrum, DOWN, buff=0)

        plank = Rectangle(width=9.5, height=0.12, fill_color=GREY_A, fill_opacity=1, stroke_width=0)
        plank.move_to(pivot + RIGHT * (4.75 - 2.4) + UP * 0.06)

        big = Square(1.7, fill_color=C_ASSET, fill_opacity=0.9, stroke_color=C_ASSET)
        big.move_to(plank.get_left() + RIGHT * 0.95 + UP * (0.06 + 0.85))
        small = Square(0.6, fill_color=C_CAP, fill_opacity=0.9, stroke_color=C_CAP)
        small.move_to(plank.get_right() + LEFT * 0.4 + UP * (0.06 + 0.3))

        beam = VGroup(plank, big, small)
        beam.rotate(0.17, about_point=pivot)

        big_lbl = T(big_text, 26, color=BLACK)
        big_lbl.add_updater(lambda m: m.move_to(big.get_center()))
        small_lbl = VGroup(T(small_text, 26, color=C_CAP))
        if small_sub:
            small_lbl.add(T(small_sub, 20, color=C_MUTED))
            small_lbl.arrange(DOWN, buff=0.08)
        small_lbl.add_updater(lambda m: m.next_to(small, UP, buff=0.2))
        extra = VGroup()
        if big_sub:
            bsub = T(big_sub, 22, color=C_ASSET)
            bsub.add_updater(lambda m: m.next_to(big, UP, buff=0.2))
            extra.add(bsub)
        return dict(pivot=pivot, fulcrum=fulcrum, ground=ground, beam=beam,
                    big=big, small=small, big_lbl=big_lbl, small_lbl=small_lbl, extra=extra)

    def make_house(self):
        body = Square(1.6, fill_color=C_ASSET, fill_opacity=0.25, stroke_color=C_ASSET, stroke_width=4)
        roof = Polygon(body.get_corner(UL) + LEFT * 0.25, body.get_corner(UR) + RIGHT * 0.25,
                       body.get_top() + UP * 0.9, color=C_ASSET, fill_color=C_ASSET,
                       fill_opacity=0.6, stroke_width=4)
        door = Rectangle(width=0.4, height=0.7, fill_color=C_ASSET, fill_opacity=0.8, stroke_width=0)
        door.move_to(body.get_bottom(), aligned_edge=DOWN)
        win = Square(0.35, stroke_color=C_ASSET, stroke_width=3).move_to(body.get_center() + UP * 0.25 + RIGHT * 0.4)
        return VGroup(body, roof, door, win)

    def hbar(self, value, color, label, y, scale=1 / 330, x0=-1.2):
        bar = Rectangle(width=value * scale, height=0.55, fill_color=color, fill_opacity=0.85,
                        stroke_width=0)
        bar.move_to(np.array([x0, y, 0]), aligned_edge=LEFT)
        name = T(label, 26).next_to(bar, LEFT, buff=0.3)
        name.align_to(np.array([x0 - 0.3, 0, 0]), RIGHT)
        val = T(brl(value), 26, color=color).next_to(bar, RIGHT, buff=0.25)
        return bar, name, val

    # ------------------------------------------------------------------
    # Roteiro
    # ------------------------------------------------------------------
    def construct(self):
        random.seed(7)
        self.intro()
        self.what_is()
        self.installment()
        self.vs_financing()
        self.bid()
        self.lever_in_action()
        self.amplification()
        self.risks()
        self.summary()
        self.end_caption()
        self.write_outputs()

    # 0 ---------------------------------------------------------------
    def intro(self):
        self.section("Abertura")
        title = T("Alavancagem com Consórcio", 60)
        sub = T("a matemática por trás da carta de crédito", 32, color=C_MUTED)
        VGroup(title, sub).arrange(DOWN, buff=0.35).move_to(UP * 0.5)
        self.play(Write(title), run_time=2)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(sub))

        L = self.make_lever("Ativo", "Seu capital")
        self.say("Arquimedes teria dito: “Dê-me uma alavanca e um ponto de apoio, e eu moverei o mundo.”")
        self.play(Create(L["ground"]), FadeIn(L["fulcrum"]))
        self.play(FadeIn(L["beam"]), FadeIn(L["big_lbl"]), FadeIn(L["small_lbl"]))
        self.wait(1)

        push = Arrow(L["small"].get_top() + UP * 2.0 + RIGHT * 0.6, L["small"].get_top() + UP * 0.9 + RIGHT * 0.6,
                     color=C_CAP, buff=0, stroke_width=6)
        push_lbl = T("força pequena", 24, color=C_CAP).next_to(push, LEFT, buff=0.2)
        self.say("Em finanças a ideia é a mesma: usar uma força pequena — o seu capital — para mover algo muito maior.")
        self.play(GrowArrow(push), FadeIn(push_lbl))
        self.play(Rotate(L["beam"], angle=-0.34, about_point=L["pivot"]),
                  push.animate.shift(DOWN * 1.1), push_lbl.animate.shift(DOWN * 1.1),
                  run_time=2.2, rate_func=smooth)
        self.wait(0.5)

        self.say("Hoje vamos ver como o consórcio pode funcionar como essa alavanca… e onde ela pode quebrar.")
        self.wait(1)
        L["big_lbl"].clear_updaters()
        L["small_lbl"].clear_updaters()
        self.clear_stage()

    # 1 ---------------------------------------------------------------
    def what_is(self):
        self.section("O que é um consórcio")
        dots = VGroup(*[Dot(radius=0.075, color=BLUE_D) for _ in range(PRAZO)])
        dots.arrange_in_grid(rows=12, cols=15, buff=0.17).move_to(LEFT * 3.2 + UP * 0.55)
        grid_lbl = T("180 participantes", 28).next_to(dots, UP, buff=0.3)

        self.say("Imagine um grupo de pessoas que querem comprar o mesmo bem, mas nenhuma tem o dinheiro todo agora.")
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.01, run_time=2))
        self.play(FadeIn(grid_lbl))

        pot = RoundedRectangle(width=4.2, height=2.0, corner_radius=0.3, color=C_GOOD)
        pot.move_to(RIGHT * 3.4 + UP * 0.9)
        pot_lbl = T("Fundo comum", 28, color=C_GOOD).next_to(pot, UP, buff=0.25)
        vt = ValueTracker(0)
        counter = always_redraw(lambda: T(brl(vt.get_value()), 34).move_to(pot.get_center()))

        self.say("Todo mês, cada participante paga uma parcela. O dinheiro vai para um fundo comum.")
        self.play(Create(pot), FadeIn(pot_lbl), FadeIn(counter))
        copies = VGroup(*[d.copy() for d in dots])
        self.add(copies)
        self.play(
            LaggedStart(*[c.animate.move_to(pot.get_center()).set_opacity(0) for c in copies],
                        lag_ratio=0.006, run_time=2.5),
            vt.animate(run_time=2.5).set_value(TOTAL),
        )
        self.remove(copies)
        eq = T("180 × R$ 2.000 = R$ 360.000 por mês", 24, color=C_MUTED).next_to(pot, DOWN, buff=0.3)
        self.play(FadeIn(eq, shift=UP * 0.1))

        lucky = dots[52]
        card = RoundedRectangle(width=3.0, height=1.5, corner_radius=0.15, color=C_ASSET,
                                fill_color=C_ASSET, fill_opacity=0.12)
        card_txt = VGroup(T("Carta de crédito", 24, color=C_ASSET), T(brl(CARTA), 34)).arrange(DOWN, buff=0.15)
        card_g = VGroup(card, card_txt).move_to(pot)
        self.say("E todo mês ao menos um participante é contemplado: recebe uma carta de crédito para comprar o bem.")
        self.play(lucky.animate.set_color(C_ASSET).scale(2.2), Flash(lucky, color=C_ASSET))
        self.play(FadeOut(counter), FadeIn(card_g, scale=0.6))
        self.play(card_g.animate.scale(0.75).next_to(eq, DOWN, buff=0.3))
        arrow = CurvedArrow(card_g.get_left() + LEFT * 0.1, lucky.get_right() + RIGHT * 0.15,
                            color=C_ASSET, angle=-TAU / 8)
        self.play(Create(arrow))

        how = VGroup(T("por sorteio", 26, color=C_MUTED), T("ou", 24, color=C_MUTED),
                     T("por lance", 26, color=C_ASSET)).arrange(RIGHT, buff=0.3)
        how.next_to(dots, DOWN, buff=0.3)
        self.say("A contemplação acontece por sorteio… ou por lance: quem oferece antecipar mais dinheiro passa na frente.")
        self.play(FadeIn(how[0]))
        self.play(FadeIn(how[1]), FadeIn(how[2]))
        self.wait(0.5)

        split = VGroup(
            T("Sem juros.", 24, color=C_GOOD),
            T("Custo: taxa de administração", 22),
            T("+ fundo de reserva", 22),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to(pot.get_center())
        self.say("Não há juros. O custo é a taxa de administração, mais um pequeno fundo de reserva.")
        self.play(FadeIn(split))
        self.wait(1)

        month_vt = ValueTracker(1)
        month = always_redraw(lambda: T(f"Mês {int(month_vt.get_value())}", 30, color=C_ASSET)
                              .to_corner(UR, buff=0.5))
        others = [d for i, d in enumerate(dots) if i != 52]
        random.shuffle(others)
        self.say("No fim do prazo todos terão sido contemplados. A pergunta que importa é: quando chega a sua vez?")
        self.play(FadeOut(arrow), FadeOut(how), FadeIn(month))
        self.play(
            LaggedStart(*[d.animate.set_color(C_ASSET) for d in others], lag_ratio=0.03, run_time=5),
            month_vt.animate(run_time=5, rate_func=linear).set_value(PRAZO),
        )
        self.wait(0.5)
        self.clear_stage()

    # 2 ---------------------------------------------------------------
    def installment(self):
        self.section("A conta da parcela")
        tc = {"Carta": C_ASSET, "taxa adm.": C_COST, "fundo de reserva": C_COST, "prazo": C_CAP}
        l1 = T("Parcela = Carta × (1 + taxa adm. + fundo de reserva) ÷ prazo", 34, t2c=tc)
        l2 = T("= 300.000 × (1 + 18% + 2%) ÷ 180", 34,
               t2c={"300.000": C_ASSET, "18%": C_COST, "2%": C_COST, "180": C_CAP})
        l3 = T("= 360.000 ÷ 180", 34, t2c={"180": C_CAP})
        l4 = T("= R$ 2.000 por mês", 40, color=C_ASSET)
        lines = VGroup(l1, l2, l3, l4).arrange(DOWN, buff=0.45).move_to(UP * 0.9)
        for l in (l2, l3, l4):
            l.align_to(l1, LEFT).shift(RIGHT * 1.85)

        self.say("Vamos aos números. Uma carta de crédito de R$ 300 mil, paga em 180 meses.")
        self.play(Write(l1), run_time=2.5)
        self.say("Taxa de administração de 18% e fundo de reserva de 2%, cobrados sobre o prazo inteiro.")
        self.play(FadeIn(l2, shift=DOWN * 0.2))
        self.say("Total a pagar: R$ 360 mil. Dividido por 180 meses, R$ 2.000 por mês.")
        self.play(FadeIn(l3, shift=DOWN * 0.2))
        self.play(FadeIn(l4, shift=DOWN * 0.2))
        self.play(Circumscribe(l4, color=C_ASSET))

        note = T("custo: 20% em 15 anos  ≈  1,3% ao ano", 30, color=C_GOOD).next_to(lines, DOWN, buff=0.5)
        self.say("Repare: o custo de 20% fica diluído em 15 anos — algo como 1,3% ao ano, em termos simples.")
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1)
        self.clear_stage()

    # 3 ---------------------------------------------------------------
    def vs_financing(self):
        self.section("Consórcio × financiamento")
        k = 0.85 / 100_000
        base_y = -2.0
        xs = [-2.3, 2.3]
        vals = [(CARTA, JUROS_SAC), (CARTA, CARTA * (TAXA_ADM + FUNDO_RES))]
        names = ["Financiamento\n11% ao ano", "Consórcio\ntaxa de 20%"]
        cost_names = ["juros", "taxas"]
        groups = []
        for x, (p, c), n, cn in zip(xs, vals, names, cost_names):
            pb = Rectangle(width=1.8, height=p * k, fill_color=C_CAP, fill_opacity=0.8, stroke_width=0)
            pb.move_to(np.array([x, base_y, 0]), aligned_edge=DOWN)
            cb = Rectangle(width=1.8, height=c * k, fill_color=C_COST, fill_opacity=0.85, stroke_width=0)
            cb.next_to(pb, UP, buff=0)
            pl = T("crédito\n" + brl(p), 22).move_to(pb)
            cl = T(f"{cn}\n≈ {brl(round(c, -3))}", 22).next_to(cb, RIGHT, buff=0.25)
            tot = T("total " + brl(round(p + c, -3)), 24, color=C_MUTED).next_to(cb, UP, buff=0.15)
            nl = T(n, 24).next_to(pb, LEFT, buff=0.3)
            groups.append((pb, cb, pl, cl, tot, nl))
        axis = Line(LEFT * 5.5, RIGHT * 5.5, color=GREY_D).move_to(np.array([0, base_y, 0]))

        self.say("Compare com um financiamento do mesmo valor e do mesmo prazo, a juros de 11% ao ano.")
        self.play(Create(axis))
        for pb, cb, pl, cl, tot, nl in groups:
            self.play(GrowFromEdge(pb, DOWN), FadeIn(pl), FadeIn(nl), run_time=1)

        pb, cb, pl, cl, tot, nl = groups[0]
        self.say(f"No financiamento, os juros compostos somam cerca de R$ {round(JUROS_SAC / 1000):.0f} mil.")
        self.play(GrowFromEdge(cb, DOWN), FadeIn(cl), FadeIn(tot), run_time=1.5)
        pb, cb, pl, cl, tot, nl = groups[1]
        self.say("No consórcio, o custo total fica em R$ 60 mil. Quase quatro vezes menos.")
        self.play(GrowFromEdge(cb, DOWN), FadeIn(cl), FadeIn(tot), run_time=1.5)
        self.wait(0.5)

        self.say("Mas existe um preço escondido. No financiamento, você recebe o dinheiro hoje. No consórcio, você espera.")
        self.wait(1)
        self.clear_stage()

        a = T("juros", 64, color=C_COST)
        arrow = T("⇄", 64, color=WHITE)
        b = T("tempo", 64, color=C_CAP)
        row = VGroup(a, arrow, b).arrange(RIGHT, buff=0.6).move_to(UP * 0.6)
        head = T("O consórcio troca", 36, color=C_MUTED).next_to(row, UP, buff=0.5)
        self.say("Em outras palavras: o consórcio troca juros por tempo.")
        self.play(FadeIn(head), FadeIn(a), FadeIn(arrow), FadeIn(b))
        self.play(Swap(a, b), run_time=1.5)
        self.wait(1)
        self.clear_stage()

    # 4 ---------------------------------------------------------------
    def bid(self):
        self.section("O lance: comprando tempo")
        line = Line(LEFT * 5.5, RIGHT * 5.5, color=GREY_B).shift(DOWN * 0.9)

        def mx(m):
            return line.point_from_proportion(m / PRAZO)

        ticks = VGroup()
        for m in range(0, PRAZO + 1, 30):
            tk = Line(UP * 0.1, DOWN * 0.1, color=GREY_B).move_to(mx(m))
            ticks.add(tk, T(str(m), 22, color=C_MUTED).next_to(tk, DOWN, buff=0.15))
        unit = T("meses", 22, color=C_MUTED).next_to(line.get_end(), DOWN, buff=0.6)
        uni = Rectangle(width=line.get_length(), height=1.3, fill_color=BLUE_E, fill_opacity=0.5,
                        stroke_color=C_CAP, stroke_width=2).next_to(line, UP, buff=0)
        uni_lbl = T("sorteio: todo mês tem a mesma chance", 26, color=C_CAP).next_to(uni, UP, buff=0.2).align_to(uni, LEFT)

        self.say("Se a contemplação fosse puro sorteio, qualquer mês do prazo seria igualmente provável.")
        self.play(Create(line), FadeIn(ticks), FadeIn(unit))
        self.play(GrowFromEdge(uni, DOWN), FadeIn(uni_lbl))

        marker = Triangle(fill_color=C_ASSET, fill_opacity=1, stroke_width=0).scale(0.18).rotate(PI)
        marker.next_to(mx(40), UP, buff=0)
        self.add(marker)
        for m in [131, 17, 99, 164, 58, 122, 76]:
            self.play(marker.animate.next_to(mx(m), UP, buff=0), run_time=0.3)

        avg_lbl = T("em média: mês 90 ≈ 7,5 anos", 28, color=C_ASSET)
        self.say("Em média, você esperaria metade do prazo: 90 meses. Sete anos e meio sem o bem.")
        self.play(marker.animate.next_to(mx(90), UP, buff=0))
        vline = DashedLine(mx(90), mx(90) + UP * 2.1, color=C_ASSET)
        avg_lbl.next_to(vline.get_end(), UP, buff=0.15)
        self.play(Create(vline), FadeIn(avg_lbl))
        self.wait(0.5)

        self.say("O lance é a forma de comprar esse tempo: você antecipa parte do saldo e passa na frente da fila.")
        self.play(FadeOut(uni), FadeOut(uni_lbl), FadeOut(vline), FadeOut(avg_lbl))
        bid_lbl = VGroup(T("lance de 25% = R$ 75.000", 28, color=C_GOOD),
                         T("contemplado no mês 3", 28, color=C_ASSET)).arrange(DOWN, buff=0.15)
        self.say("Suponha um lance de 25% da carta, ou seja, R$ 75 mil. Com ele, você é contemplado já no 3º mês.")
        self.play(marker.animate.next_to(mx(MES_CONTEMPLA), UP, buff=0).set_color(C_GOOD), run_time=1.5)
        bid_lbl.next_to(marker, UP, buff=0.4).align_to(marker, LEFT).shift(LEFT * 0.2)
        saved = DoubleArrow(mx(MES_CONTEMPLA) + DOWN * 0.9, mx(90) + DOWN * 0.9, buff=0, color=C_CAP,
                            stroke_width=4, tip_length=0.2)
        saved_lbl = T("≈ 7 anos antecipados", 24, color=C_CAP).next_to(saved, DOWN, buff=0.12)
        self.play(FadeIn(bid_lbl, shift=UP * 0.2))
        self.play(GrowFromCenter(saved), FadeIn(saved_lbl))
        self.wait(1)
        self.clear_stage()

        tc = {"75.000": C_GOOD, "279.000": C_ASSET, "177": C_CAP}
        s1 = T("Saldo = 360.000 − 3 × 2.000 − 75.000", 34, t2c=tc)
        s2 = T("= R$ 279.000", 34, t2c=tc)
        s3 = T("Nova parcela = 279.000 ÷ 177 meses", 34, t2c=tc)
        s4 = T(f"≈ {brl(NOVA_PARCELA)} por mês", 40, color=C_ASSET)
        g = VGroup(s1, s2, s3, s4).arrange(DOWN, buff=0.4).move_to(UP * 0.7)
        s2.align_to(s1, LEFT).shift(RIGHT * 1.6)
        s4.align_to(s3, LEFT).shift(RIGHT * 2.3)
        self.say("O lance abate o saldo devedor. Restam R$ 279 mil, a pagar nos 177 meses seguintes.")
        self.play(Write(s1), run_time=2)
        self.play(FadeIn(s2, shift=DOWN * 0.2))
        self.say(f"A parcela cai de R$ 2.000 para cerca de R$ {NOVA_PARCELA:,.0f}.".replace(",", "."))
        self.play(FadeIn(s3, shift=DOWN * 0.2))
        self.play(FadeIn(s4, shift=DOWN * 0.2))
        self.play(Circumscribe(s4, color=C_ASSET))

        emb = T("lance embutido: usa parte da própria carta → crédito menor", 26, color=C_MUTED)
        emb.next_to(g, DOWN, buff=0.5)
        self.say("Há também o lance embutido, que usa parte da própria carta. Ele exige menos dinheiro, mas reduz o crédito recebido.")
        self.play(FadeIn(emb))
        self.wait(1)
        self.clear_stage()

    # 5 ---------------------------------------------------------------
    def lever_in_action(self):
        self.section("A alavanca em ação")
        house = self.make_house().scale(0.9).move_to(LEFT * 4.3 + UP * 1.3)
        h_lbl = T("Imóvel  " + brl(CARTA), 28, color=C_ASSET).next_to(house, DOWN, buff=0.25)
        card = RoundedRectangle(width=2.6, height=1.3, corner_radius=0.15, color=C_ASSET,
                                fill_color=C_ASSET, fill_opacity=0.12)
        card_txt = VGroup(T("Carta de crédito", 22, color=C_ASSET), T(brl(CARTA), 30)).arrange(DOWN, buff=0.12)
        card_g = VGroup(card, card_txt).move_to(house)

        self.say("Agora a carta de crédito vira um imóvel de R$ 300 mil, que é colocado para alugar.")
        self.play(FadeIn(card_g, scale=0.7))
        self.wait(0.4)
        self.play(ReplacementTransform(card_g, house), FadeIn(h_lbl), run_time=1.5)

        rent_arrow = Arrow(house.get_right() + RIGHT * 0.4, house.get_right() + RIGHT * 2.9, color=C_GOOD, buff=0)
        rent_lbl = T("aluguel: 0,5% ao mês", 24, color=C_GOOD).next_to(rent_arrow, UP, buff=0.15)
        rent_val = T(brl(ALUGUEL), 32, color=C_GOOD).next_to(rent_arrow, RIGHT, buff=0.25)
        self.say("Com um aluguel de 0,5% ao mês, o imóvel rende R$ 1.500 por mês.")
        self.play(GrowArrow(rent_arrow), FadeIn(rent_lbl))
        self.play(FadeIn(rent_val, shift=RIGHT * 0.2))

        x0 = -1.2
        pb, pn, pv = self.hbar(NOVA_PARCELA, C_COST, "parcela", -0.9, x0=x0)
        ab, an, av = self.hbar(ALUGUEL, C_GOOD, "aluguel", -1.7, x0=x0)
        gap = Rectangle(width=pb.width - ab.width, height=0.55, stroke_color=WHITE, stroke_width=2,
                        fill_opacity=0).move_to(np.array([ab.get_right()[0] + (pb.width - ab.width) / 2, -1.7, 0]))
        av.next_to(gap, RIGHT, buff=0.25)
        gap_lbl = T(f"≈ {brl(GAP)}/mês do seu bolso", 24).next_to(av, RIGHT, buff=0.35)

        self.say(f"O aluguel paga quase toda a parcela. A diferença, cerca de R$ {GAP:.0f} por mês, sai do seu bolso.")
        self.play(GrowFromEdge(pb, LEFT), FadeIn(pn), FadeIn(pv))
        self.play(TransformFromCopy(rent_val, ab), FadeIn(an), FadeIn(av))
        self.play(Create(gap), FadeIn(gap_lbl))
        self.wait(1)
        self.clear_stage()

        L = self.make_lever("R$ 300 mil", "R$ 81 mil", big_sub="imóvel", small_sub="seu capital")
        self.say("Quanto dinheiro seu entrou até aqui? R$ 75 mil de lance mais 3 parcelas de R$ 2.000: R$ 81 mil.")
        breakdown = T("75.000 (lance) + 3 × 2.000 (parcelas) = R$ 81.000", 28,
                      t2c={"R$ 81.000": C_CAP}).to_edge(UP, buff=0.5)
        self.play(FadeIn(breakdown))
        self.play(Create(L["ground"]), FadeIn(L["fulcrum"]), FadeIn(L["beam"]),
                  FadeIn(L["big_lbl"]), FadeIn(L["small_lbl"]), FadeIn(L["extra"]))
        lev = T(f"alavancagem = 300 ÷ 81 ≈ {LEV:.1f}×".replace(".", ","), 36, color=C_ASSET)
        lev.next_to(breakdown, DOWN, buff=0.4)
        self.say("Com R$ 81 mil seus, você controla um ativo de R$ 300 mil: uma alavancagem de 3,7 vezes.")
        self.play(Rotate(L["beam"], angle=-0.34, about_point=L["pivot"]), run_time=2)
        self.play(Write(lev))
        self.wait(1)
        for m in (L["big_lbl"], L["small_lbl"], *L["extra"]):
            m.clear_updaters()
        self.clear_stage()

    # 6 ---------------------------------------------------------------
    def amplification(self):
        self.section("A matemática da alavancagem")
        ax = Axes(x_range=[-20, 20, 5], y_range=[-80, 80, 20], x_length=7, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2})
        ax.move_to(LEFT * 2.6 + UP * 0.45)
        labels = VGroup()
        for x in (-20, -10, 10, 20):
            labels.add(T(f"{x:+d}%", 18, color=C_MUTED).next_to(ax.c2p(x, 0), DOWN, buff=0.15))
        for y in (-80, -40, 40, 80):
            labels.add(T(f"{y:+d}%", 18, color=C_MUTED).next_to(ax.c2p(0, y), LEFT, buff=0.15))
        xl = T("variação do imóvel", 22, color=C_MUTED).next_to(ax.c2p(20, 0), DOWN, buff=0.5).align_to(ax.c2p(20, 0), RIGHT)
        yl = T("retorno sobre o seu capital", 22, color=C_MUTED).next_to(ax.y_axis, UP, buff=0.1)

        g1 = ax.plot(lambda x: x, color=GREY_A, stroke_width=3)
        g2 = ax.plot(lambda x: LEV * x, x_range=[-20, 20], color=C_ASSET, stroke_width=4)
        g1_lbl = T("à vista (1×)", 22, color=GREY_A).next_to(ax.c2p(20, 20), RIGHT, buff=0.1)
        g2_lbl = T("consórcio (3,7×)", 22, color=C_ASSET).next_to(ax.c2p(20, 74), RIGHT, buff=0.1)

        self.say("Agora a parte mais importante: o que a alavancagem faz com o seu retorno.")
        self.play(Create(ax), FadeIn(labels), FadeIn(xl), FadeIn(yl))
        self.play(Create(g1), FadeIn(g1_lbl))
        self.play(Create(g2), FadeIn(g2_lbl))

        xv = ValueTracker(0)
        d1 = always_redraw(lambda: Dot(ax.c2p(xv.get_value(), xv.get_value()), color=GREY_A))
        d2 = always_redraw(lambda: Dot(ax.c2p(xv.get_value(), LEV * xv.get_value()), color=C_ASSET))
        vline = always_redraw(lambda: DashedLine(ax.c2p(xv.get_value(), 0),
                                                 ax.c2p(xv.get_value(), LEV * xv.get_value()),
                                                 color=GREY_C, stroke_width=2))

        def panel():
            v = xv.get_value()
            col = C_GOOD if v >= 0 else C_COST
            rows = VGroup(
                T(f"imóvel: {pct(v)}", 26, color=WHITE),
                T(f"ganho: {brl(abs(v) / 100 * CARTA)}" if v >= 0 else f"perda: {brl(abs(v) / 100 * CARTA)}", 24, color=C_MUTED),
                T(f"à vista: {pct(v)}", 26, color=GREY_A),
                T(f"consórcio: {pct(LEV * v)}", 30, color=col),
            ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            return rows.move_to(RIGHT * 4.95 + UP * 0.6)

        readout = always_redraw(panel)
        self.add(vline, d1, d2, readout)

        self.say("Se o imóvel valoriza 5%, são R$ 15 mil de ganho. Sobre os seus R$ 81 mil, isso é 18,5%.")
        self.play(xv.animate.set_value(5), run_time=2.5)
        self.wait(0.5)
        self.say("Quem comprou à vista, com R$ 300 mil, teve os mesmos R$ 15 mil de ganho: apenas 5%.")
        self.play(Indicate(d1, color=GREY_A))
        self.wait(0.5)

        rule = T("retorno ≈ alavancagem × variação do ativo", 26, color=C_ASSET).to_edge(UP, buff=0.25)
        self.say("Essa é a alavanca: o mesmo movimento do ativo, multiplicado pela razão entre o ativo e o seu capital.")
        self.play(FadeIn(rule, shift=DOWN * 0.2))
        self.wait(1)

        self.say("Mas a alavanca funciona nos dois sentidos.")
        self.play(xv.animate.set_value(0), run_time=1.5)
        self.say("Se o imóvel cai 10%, a perda de R$ 30 mil representa 37% de todo o capital que você colocou.")
        self.play(xv.animate.set_value(-10), run_time=2.5)
        self.play(Flash(d2, color=C_COST, flash_radius=0.4))
        self.wait(1)
        self.clear_stage()

    # 7 ---------------------------------------------------------------
    def risks(self):
        self.section("Onde a alavanca pode quebrar")
        title = T("Onde a alavanca pode quebrar", 42, color=C_COST).to_edge(UP, buff=0.5)
        items = [
            ("Correção anual", "carta e parcelas sobem com o INCC ou o IPCA",
             "Correção: a carta e as parcelas são corrigidas todo ano por um índice, como o INCC ou o IPCA."),
            ("Vacância", "sem inquilino, a parcela inteira sai do seu bolso",
             "Vacância: sem inquilino, a parcela inteira volta a sair do seu bolso."),
            ("Incerteza", "o lance pode não ser suficiente para contemplar",
             "Incerteza: outros participantes também dão lances. O seu pode não ser suficiente."),
            ("Liquidez", "dinheiro preso; sair do grupo antes do fim é caro",
             "Liquidez: o dinheiro fica preso, e desistir do grupo antes do fim costuma sair caro."),
        ]
        rows = VGroup()
        for i, (h, d, _) in enumerate(items, 1):
            num = VGroup(Circle(0.28, color=C_COST, fill_opacity=0.15), T(str(i), 26, color=C_COST))
            txt = VGroup(T(h, 30), T(d, 24, color=C_MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            rows.add(VGroup(num, txt).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32).next_to(title, DOWN, buff=0.5)

        self.say("Toda alavanca tem um ponto de ruptura. No consórcio, os principais são quatro.")
        self.play(FadeIn(title))
        for row, (_, _, cap) in zip(rows, items):
            self.say(cap)
            self.play(FadeIn(row, shift=RIGHT * 0.3))
        self.wait(0.5)
        self.clear_stage()

        x0 = -1.2
        pb, pn, pv = self.hbar(NOVA_PARCELA, C_COST, "parcela", 0.9, x0=x0)
        ab, an, av = self.hbar(ALUGUEL, C_GOOD, "aluguel", 0.1, x0=x0)
        gap = always_redraw(lambda: Rectangle(
            width=max(pb.get_right()[0] - ab.get_right()[0], 0.01), height=0.55,
            stroke_color=WHITE, stroke_width=2).move_to(
            np.array([(pb.get_right()[0] + ab.get_right()[0]) / 2, 0.1, 0])))
        rent = ValueTracker(ALUGUEL)
        av = always_redraw(lambda: T(brl(rent.get_value()), 26, color=C_GOOD)
                           .next_to(np.array([pb.get_right()[0], 0.1, 0]), RIGHT, buff=0.25))
        gl = always_redraw(lambda: T(f"buraco mensal: {brl(NOVA_PARCELA - rent.get_value())}", 30)
                           .move_to(DOWN * 1.1))
        head = T("Exemplo: 2 meses de vacância por ano", 32, color=C_ASSET).to_edge(UP, buff=0.8)

        self.say("Um exemplo: com dois meses de imóvel vazio por ano, o aluguel efetivo cai para R$ 1.250.")
        self.play(FadeIn(head))
        self.add(pb, pn, pv, ab, an, gap, av, gl)
        self.play(*[FadeIn(m) for m in (pb, pn, pv, ab, an)])
        scale = 1 / 330
        self.play(rent.animate.set_value(ALUGUEL_VAC),
                  ab.animate.stretch_to_fit_width(ALUGUEL_VAC * scale, about_edge=LEFT), run_time=2)
        self.say(f"E o buraco mensal salta de R$ {GAP:.0f} para R$ {GAP_VAC:.0f}. Pequenas mudanças, grandes efeitos.")
        self.play(Indicate(gl, color=C_COST))
        self.wait(1)
        self.clear_stage()

    # 8 ---------------------------------------------------------------
    def summary(self):
        self.section("Resumo")
        lines = VGroup(
            T("Consórcio: troca juros por tempo", 36, t2c={"juros": C_COST, "tempo": C_CAP}),
            T("Lance: compra tempo com o seu capital", 36, t2c={"tempo": C_CAP, "capital": C_CAP}),
            T("Alavancagem = ativo ÷ capital próprio", 36, t2c={"ativo": C_ASSET, "capital próprio": C_CAP}),
            T("Ela multiplica os ganhos… e as perdas", 36, t2c={"ganhos": C_GOOD, "perdas": C_COST}),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to(UP * 0.6)

        self.say("Resumindo: o consórcio troca juros por tempo, e o lance compra esse tempo com o seu capital.")
        self.play(FadeIn(lines[0], shift=UP * 0.2))
        self.play(FadeIn(lines[1], shift=UP * 0.2))
        self.say("A alavancagem é a razão entre o ativo e o seu capital, e ela multiplica o resultado — para cima e para baixo.")
        self.play(FadeIn(lines[2], shift=UP * 0.2))
        self.play(FadeIn(lines[3], shift=UP * 0.2))
        self.say("Antes de puxar a alavanca, faça as contas: custos, prazos, correção e o pior cenário.")
        self.play(Circumscribe(lines[3], color=C_ASSET))
        self.wait(1)
        self.clear_stage()

        disc = T("Conteúdo educativo. Valores ilustrativos e simplificados.\nNão é recomendação de investimento.",
                 26, color=C_MUTED, line_spacing=1.0)
        self.say("Valores ilustrativos e simplificados. Este vídeo é educativo e não é recomendação de investimento.")
        self.play(FadeIn(disc))
        self.wait(2)
        self.end_caption()
        self.play(FadeOut(disc))
        self.wait(0.5)
