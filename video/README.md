# Alavancagem com Consórcio — vídeo explicativo

Vídeo no estilo 3Blue1Brown (fundo escuro, fonte CMU Serif, animações com [Manim](https://www.manim.community/)),
**sem narração**: as falas do roteiro aparecem como legendas na parte inferior da tela.

| Arquivo | Conteúdo |
|---|---|
| `alavancagem_consorcio.mp4` | Vídeo final, 1920×1080, 30 fps, legendas embutidas |
| `alavancagem_consorcio.srt` | As mesmas legendas com tempos, para a narração ou para usar como legenda separada |
| `roteiro.md` | Roteiro completo por seção, com a minutagem |
| `alavancagem_consorcio.py` | Código-fonte da animação |

## Estrutura

1. **Abertura**: a alavanca de Arquimedes como metáfora.
2. **O que é um consórcio**: 180 participantes, o fundo comum e a contemplação por sorteio ou por lance.
3. **A conta da parcela**: R$ 300 mil × (1 + 18% + 2%) ÷ 180 = R$ 2.000/mês.
4. **Consórcio × financiamento**: R$ 60 mil de taxas contra ≈ R$ 237 mil de juros (11% a.a., SAC). O consórcio troca juros por tempo.
5. **O lance**: com sorteio puro, a espera média é de 90 meses. Um lance de 25% leva à contemplação no mês 3, e a parcela cai para ≈ R$ 1.576.
6. **A alavanca em ação**: o imóvel alugado a 0,5% a.m. (R$ 1.500) quase paga a parcela. R$ 81 mil de capital próprio controlam R$ 300 mil (3,7×).
7. **A matemática da alavancagem**: no gráfico, +5% no imóvel vira +18,5% sobre o seu capital, e −10% vira −37%.
8. **Riscos**: correção (INCC/IPCA), vacância, incerteza do lance e liquidez. Com 2 meses de vacância por ano, a diferença mensal vai de R$ 76 para R$ 326.
9. **Resumo** e aviso legal.

## Como renderizar

Requer Python 3, Manim Community (`pip install manim`, que depende de cairo/pango), ffmpeg e a fonte
CMU Serif (`apt install fonts-cmu`). Não precisa de LaTeX.

```bash
manim -r 1920,1080 --frame_rate 30 alavancagem_consorcio.py AlavancagemConsorcio
```

A renderização também regenera `alavancagem_consorcio.srt` e `roteiro.md`. Para pôr a narração depois,
grave seguindo o `.srt`. O tempo de cada legenda vem da velocidade de leitura (cerca de 15 caracteres por segundo).

> Valores ilustrativos e simplificados (sem correção monetária, seguros ou impostos).
> Conteúdo educativo, não é recomendação de investimento.
