# State-Space Anatomy of the Waiting Hall（待合広場の状態空間解剖）

待合広場（waiting hall）の内部 ―― あるトラジェクトリが `remaining_K` バンドから**最初に出口を出る前**に
いる空間 ―― がどんな形をしているかを調べた、有限サンプルの観察的な章です。

> やさしい入口：ある数の通り道を「駅の構内」にたとえます。出口（改札）から
> どれくらい手前にいるかを `exit_distance` という「距離」で表し、その距離ごとに
> 何が起きているかを地図にします。これは観察の地図であって、原因や証明ではありません。

---

## 概要

中心となる座標は **`exit_distance`**（出口層からどれくらい手前にいるか）です。この距離に沿って読むと、
待合広場は「出口の手前のひとつの境界」ではなく、いくつかの区域が積み重なった小さな**状態空間（state space）**
として見えてきます。具体的には、miss が出ない**出口層**（`exit_distance 0–2`）、観察された 228 件の
miss がすべて入る**miss-front**（`3–8`）、そして評価分布（k）は変化するのに miss が 0 の
**k-structure corridor**（`12–30`）の3区域です。さらに、どの単独座標も miss だけをきれいに囲えず、
miss だけの cell（miss-only cell）は「位置の座標1つ」と「局所的な形の座標1つ」を組み合わせて初めて現れます。
以上はすべて**観察**として報告するもので、規則・機構・証明ではありません。

**対象データ：** band-internal event rows 76,530 件 ／ miss events 228 件 ／ non-miss background rows 76,302 件。

---

## 主要結果

- **miss は `exit_distance 3–8`（miss-front）に集中する。** 観察された 228 件の miss はすべてこの範囲に入り、
  特に 3〜4 付近が中心。
- **`exit_distance 0–2`（出口層）には miss が出ない。**
- **`exit_distance 12–30` は k-structure corridor だが miss は 0。** この区域には 34,565 件のイベントがあり、
  miss は 0 件。なめらかな勾配ではなく、局所的な k のレジームが交互に並ぶ（15 で k3 のスパイク、
  22→23 と 26→27 で k1/k2 の反転）。
- **1座標だけでは non-miss が漏れる。** 228 件の miss をすべて含むように選んでも、どの単独座標も多数の
  non-miss background を一緒に拾ってしまう。
- **miss-only cell は2座標で初めて出る。** 可能な6つの座標ペアのうち4つが「228 miss ／ 0 non-miss」になる。
- **成功する2座標は position + shape。** miss-only になるペアは必ず、位置の座標
  （`exit_distance` または `remaining_K_before`）と局所的な形の座標
  （`residue_pair_mod32` または `transition_k`）を1つずつ組み合わせている。

区域の概観（連続 `exit_distance` で見たもの）:

| 区域 | exit_distance | events | miss | miss_rate | dominant k |
|---|---|---:|---:|---:|---:|
| 出口層（exit layer） | 0–2 | — | 0 | — | — |
| miss-front | 3–8 | 14,743 | 228 | 0.015465 | 1 |
| k-structure corridor | 12–30 | 34,565 | 0 | 0.000000 | 1 |

miss-front と corridor の区域レベルの k 分布の L1 差は `0.16214`：両者は k では近いが、miss の有無で決定的に異なります。

---

## この章が主張しないこと

これは有限サンプルの、band 内部のイベントに限った観察です。次のいずれも**主張しません**。

- 機構や原因（`exit_distance` や residue は**座標**であって、原因ではありません）。
- いかなる種類の証明。
- 反例。
- コラッツ全体に関する主張。
- 区域の境目が「しきい値」であること（区域は**記述的なまとまり**です）。

「**miss-only selector**」の cell とは、「**この有限データの中で、miss を含み、non-miss が一件も漏れ込まなかった
cell**」という意味だけです。**規則・原因・十分条件ではありません。** このデータの外で必要・十分・機構的である、
という意味は含みません。新しい miss type は導入せず、既存の `A / B / C1 / C2 / C3 / C_unassigned` ラベルを
そのまま使います。

---

## 座標の定義

| 座標 | 種類 | 意味 |
|---|---|---|
| `exit_distance` | 位置（positional） | バンドの下端の出口層からの距離。`0` が出口、大きいほど広場の奥。`remaining_K_before − band_lower_edge` として読む。 |
| `remaining_K_before` | 位置（positional） | そのステップの前に残っている評価質量（remaining valuation mass）。 |
| `transition_k` | 局所的な形（local-shape） | そのステップの評価値 `k`。 |
| `residue_pair`（例：`mod32`） | 局所的な形（local-shape） | イベントの residue-pair 座標。 |
| miss local type | ラベル | 既存の `A / B / C1 / C2 / C3 / C_unassigned`（そのまま再利用）。 |

「near behavior」ラベル（`drift`, `wait`, `miss`, `exit`）は、位置と既存の behavior/miss の結合から導いた
**観察ラベル**であって、新しい型ではありません。

---

## 主要表

76,530 件のイベント行（miss 228 件 ／ non-miss background 76,302 件）に対する selector 監査です。
cell が「miss-only」とは、228 件の miss をすべて含み、non-miss を 0 件しか含まないことを指します。

**単独座標 ― すべて漏れる：**

| 座標 | matched | miss | non-miss | miss_rate | miss-only? |
|---|---:|---:|---:|---:|:---:|
| exit_distance | 14,743 | 228 | 14,515 | 0.015465 | no |
| remaining_K_before | 13,802 | 228 | 13,574 | 0.016519 | no |
| residue_pair_mod32 | 275 | 228 | 47 | 0.829091 | no |
| transition_k | 4,946 | 228 | 4,718 | 0.046098 | no |

漏れがもっとも少ない単独座標は `residue_pair_mod32`（non-miss 47 件）ですが、それでも miss-only ではありません。

**2座標ペア ― miss-only cell はここで初めて現れる：**

| ペア | matched | miss | non-miss | miss-only? | 組み合わせ |
|---|---:|---:|---:|:---:|---|
| exit_distance + residue_pair_mod32 | 228 | 228 | 0 | yes | position + shape |
| exit_distance + transition_k | 228 | 228 | 0 | yes | position + shape |
| remaining_K_before + residue_pair_mod32 | 228 | 228 | 0 | yes | position + shape |
| remaining_K_before + transition_k | 228 | 228 | 0 | yes | position + shape |
| residue_pair_mod32 + transition_k | 275 | 228 | 47 | no | shape + shape |
| exit_distance + remaining_K_before | 13,802 | 228 | 13,574 | no | position + position |

3座標・4座標の selector も miss-only のままですが、すでに position–shape のペアで分離できているため何も加わりません。
この監査では4座標タプルは冗長です。

---

## 図・成果物一覧

| 図 | 役割 |
|---|---|
| `waiting_hall_interior_map.png` | 粗い4箱の広場（upper / mid / lower / exit_layer） |
| `band_position_flow_map.png` | 広場の区域間の下向きの流れと出口 |
| `k_by_hall_zone_heatmap.png` | 粗い区域ごとの `k` 分布 |
| `exit_distance_miss_rate_plot.svg` | 連続 exit_distance に対する miss rate |
| `k_change_by_exit_distance.png` | 距離ごとの k-change スコア（ランドマーク 15 / 18 / 23 / 27） |
| `k_structure_corridor_heatmap.png` | `12–30` の距離ごとの `k` ヒストグラム |
| selector 図（推奨） | position × shape の miss-only cell |
| state-space 図（本章） | exit-layer / miss-front / corridor の積み重ね |

章本体：`state_space_anatomy_of_the_waiting_hall.md`。

---

## 読み方

**観察。** `exit_distance` に沿うと、待合広場は3つの区域に分かれます。出口層（`0–2`）には miss が出ません。
miss-front（`3–8`）には 228 件の miss がすべて入り、3〜4 付近に集中します。corridor（`12–30`）には
34,565 件のイベントがあり miss は 0 件で、その `k` 分布は局所的なレジームが交互に変化します。
selector 監査では、どの単独座標も miss-only にならず、miss-only cell は2座標で初めて現れ、成功するペアは
いずれも「位置の座標1つ」と「局所的な形の座標1つ」を組み合わせています。

**解釈（観察とは分けて、控えめに）。** 状態空間として読むと、広場には「どこ（where）」の軸
（exit distance / 位置）と「どう（how）」の軸（局所的な形：`k`・residue・parity）があります。
このサンプルでは、miss は位置だけ・形だけで決まるのではなく、その**両方が重なる場所**にあります。
これは境界の地図ではなく、状態空間の概念図であり、有限で miss-event-local な観察だけから組み立てたものです。
機構・因果・証明・反例・コラッツ全体への主張は一切含みません。

> やさしい言い換え：「赤い服の人」だけ、あるいは「3番出口の近く」だけでは関係ない人がたくさん混ざる。
> でも「3番出口の近く」＋「赤い服」のように、**場所の目印と見た目の目印を合わせる**と、この有限データの中では
> ピタッと miss だけが集まった。ただしこれは「見分けられた」だけで、「原因が分かった」ではありません。

---

## 元になった source reports

本 README とその章は、5本の有限サンプルレポートを、レポートごとに列挙するのではなく、ひとつの流れ
（R1 → R6）に再編成したものです。

| レポート | 対応する節 |
|---|---|
| `waiting_hall_interior_report.md` | R1 ― 粗い4箱の広場 |
| `hall_zone_comparison_report.md` | R2 ― miss-front と corridor の比較 |
| `zone_coordinate_contrast_report.md` | R2 / R4 ― k が似た距離ペア、residue/parity |
| `k_structure_corridor_report.md` | R3 ― 12–30 corridor |
| `minimal_miss_selector_report.md` | R5 ― 最小の miss-only selector |

本章は、既存の Paradoxical-Sequence 章（`64-95 → 32-63` 境界での first-pass faces）とは独立しており、
これを書き換えるものではありません。本章は**その境界の手前にある空間**を扱います。既存 README から
リンクできますが、統合や置き換えは行いません。

---

## 注意書き

上記の結果はすべて有限サンプルの観察です。「miss-only selector」の cell は、有限サンプル内で non-miss が
漏れなかった cell という意味であり、規則・原因・十分条件ではありません。機構・因果・証明・反例・コラッツ全体への
主張は一切しません。`exit_distance` や residue は座標であって原因ではなく、区域はしきい値ではなく記述的なまとまりです。
