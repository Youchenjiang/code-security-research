import os
import json
import zlib
import base64
import urllib.parse

drawio_path = r'c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\引用鏈_圖譜.drawio'
json_path = r'c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\paper_markdowns\master_exhaustive_citations.json'

with open(json_path, 'r', encoding='utf-8') as f:
    citations = json.load(f)

banners = [
    {"id": "row1", "title": "01. 理論與基礎設施層 (Gen 1)", "y": 80, "h": 160, "fill": "#fce4ec", "stroke": "#c2185b"},
    {"id": "row2", "title": "02. 早期黑箱與語意樹比對層 (Gen 2)", "y": 270, "h": 160, "fill": "#e3f2fd", "stroke": "#1976d2"},
    {"id": "row3", "title": "03. 神經網路斷言生成世代 (Neural Assertion Gen)", "y": 460, "h": 200, "fill": "#e8f5e9", "stroke": "#388e3c"},
    {"id": "row4", "title": "04. LLM 時代斷言增強世代 (LLM Oracle Gen)", "y": 690, "h": 170, "fill": "#fffde7", "stroke": "#fbc02d"},
    {"id": "row5", "title": "05. 安全基準與 LLM 評測世代 (Security Benchmarks & Agents)", "y": 890, "h": 200, "fill": "#fff3e0", "stroke": "#f57c00"}
]

nodes = {
    "01": {"name": "01. Barr et al. Survey (2015)\nTest Oracle 分類理論", "x": 300, "y": 140, "fill": "#f8bbd0", "stroke": "#c2185b"},
    "31": {"name": "31. Daikon (2007)\n動態不變量推斷", "x": 800, "y": 140, "fill": "#f8bbd0", "stroke": "#c2185b"},
    "32": {"name": "32. EvoSuite (2013)\n測試前綴生成引擎", "x": 1300, "y": 140, "fill": "#f8bbd0", "stroke": "#c2185b"},

    "02": {"name": "02. Avancini & Ceccato (2012)\nTree Kernel XSS", "x": 200, "y": 330, "fill": "#bbdefb", "stroke": "#1976d2"},
    "27": {"name": "27. Circe (2013)\nGrammar-Based Oracle", "x": 600, "y": 330, "fill": "#bbdefb", "stroke": "#1976d2"},
    "03": {"name": "03. SOFIA (2016)\nSQLi Parse Tree 比對", "x": 1000, "y": 330, "fill": "#bbdefb", "stroke": "#1976d2"},
    "28": {"name": "28. Metamorphic Sec Testing (2021)\nPastore et al. 變質測試", "x": 1450, "y": 330, "fill": "#bbdefb", "stroke": "#1976d2"},

    "22": {"name": "22. Atlas (2020)\nNMT Assert 生成", "x": 70, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},
    "23": {"name": "23. AthenaTest (2020)\nTransformer Assert", "x": 280, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},
    "24": {"name": "24. ReAssert (2020)\nReformer Assert 補全", "x": 490, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},
    "25": {"name": "25. NUTS (2021)\nAssert Unit Test", "x": 700, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},
    "34": {"name": "34. Tufano BART (2022)\nPretrained BART Assert", "x": 910, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},
    "05": {"name": "05. TOGA (ICSE 2022)\n樞紐 Transformer Oracle", "x": 1120, "y": 530, "fill": "#81c784", "stroke": "#2e7d32"},
    "17": {"name": "17. TEval+ (2023)\nTOGA 質疑評測", "x": 1330, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},
    "18": {"name": "18. Neural Eval (2023)\n大規模複製評估", "x": 1540, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},
    "26": {"name": "26. EDITAS (ASE 2023)\nRetrieve-and-Edit", "x": 1750, "y": 530, "fill": "#c8e6c9", "stroke": "#388e3c"},

    "16": {"name": "16. TECO (2023)\nDeep Semantics Test", "x": 200, "y": 760, "fill": "#fff9c4", "stroke": "#fbc02d"},
    "06": {"name": "06. TOGLL (2024)\nCode LLM + CCS", "x": 550, "y": 760, "fill": "#fff9c4", "stroke": "#fbc02d"},
    "07": {"name": "07. ChatAssert (2025)\nDynamic Feedback", "x": 900, "y": 760, "fill": "#fff9c4", "stroke": "#fbc02d"},
    "08": {"name": "08. AugmenTest (2025)\nPrefix Pre-gen", "x": 1250, "y": 760, "fill": "#fff9c4", "stroke": "#fbc02d"},
    "09": {"name": "09. AutoOracle (2026)\nC++ Filtered Synthesis", "x": 1600, "y": 760, "fill": "#fff9c4", "stroke": "#fbc02d"},

    "19": {"name": "19. SecurityEval (2022)\nCWE 漏洞資料集", "x": 60, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "33": {"name": "33. CyberSecEval (2023)\nPurple Llama 基準", "x": 250, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "29": {"name": "29. CodeSecEval (2024)\nLLM 安全評測", "x": 440, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "13": {"name": "13. CWEval (2025)\nOutcome-Driven 評測", "x": 630, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "11": {"name": "11. AutoSUIT (2026)\nDual-Track Contrastive", "x": 820, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "12": {"name": "12. SecMutBench (2026)\nCWE Mutation Intercept", "x": 1010, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "15": {"name": "15. SecAwareCoder (2026)\nTask-Adaptive Agent", "x": 1200, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "14": {"name": "14. Assertain (2026)\nSystemVerilog RTL SVA", "x": 1390, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "10": {"name": "10. IEEE Computer (2026)\nLLM Invariant Synthesis", "x": 1580, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"},
    "20": {"name": "20. LLM Oracle Roadmap\nTest Oracle Roadmap", "x": 1770, "y": 960, "fill": "#ffe0b2", "stroke": "#f57c00"}
}

# Construct inner mxGraphModel XML
inner_xml = []
inner_xml.append('<mxGraphModel dx="1422" dy="798" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2400" pageHeight="1400" math="0" shadow="0">')
inner_xml.append('  <root>')
inner_xml.append('    <mxCell id="0" />')
inner_xml.append('    <mxCell id="1" parent="0" />')

# Banners
for b in banners:
    style = f"text;html=1;strokeColor={b['stroke']};fillColor={b['fill']};verticalAlign=top;align=left;spacingLeft=15;spacingTop=8;rounded=1;shadow=0;fontColor=#333333;fontStyle=1;fontSize=14;"
    title_escaped = b['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    inner_xml.append(f'    <mxCell id="{b["id"]}" value="{title_escaped}" style="{style}" vertex="1" parent="1">')
    inner_xml.append(f'      <mxGeometry x="40" y="{b["y"]}" width="2020" height="{b["h"]}" as="geometry" />')
    inner_xml.append('    </mxCell>')

# Nodes
for pid, n in nodes.items():
    name_escaped = n['name'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '&#10;')
    style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={n['fill']};strokeColor={n['stroke']};fontStyle=1;fontSize=11;align=center;verticalAlign=middle;shadow=1;"
    inner_xml.append(f'    <mxCell id="node_{pid}" value="{name_escaped}" style="{style}" vertex="1" parent="1">')
    inner_xml.append(f'      <mxGeometry x="{n["x"]}" y="{n["y"]}" width="180" height="55" as="geometry" />')
    inner_xml.append('    </mxCell>')

# Edges
edge_idx = 1
for c in citations:
    src_id = c['from_id']
    tgt_id = c['to_id']
    ref_label = f"[{c['ref_num']}]" if c.get('ref_num') and c['ref_num'] != "Found" else ""
    
    if src_id in nodes and tgt_id in nodes:
        edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#444444;strokeWidth=1.2;endArrow=classic;endSize=5;fontSize=10;fontColor=#222222;"
        inner_xml.append(f'        <mxCell id="edge_{edge_idx}" value="{ref_label}" style="{edge_style}" edge="1" parent="1" source="node_{src_id}" target="node_{tgt_id}">')
        inner_xml.append('          <mxGeometry relative="1" as="geometry" />')
        inner_xml.append('        </mxCell>')
        edge_idx += 1

inner_xml.append('  </root>')
inner_xml.append('</mxGraphModel>')

model_str = ''.join(inner_xml)

# Standard Draw.io Compression Pipeline:
# 1. URL encode string
quoted_str = urllib.parse.quote(model_str)
# 2. Deflate compress (wbits=-15 for raw deflate)
compressed_bytes = zlib.compress(quoted_str.encode('utf-8'), level=9)[2:-4] # strip zlib wrapper or use wbits=-15
obj = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15)
compressed_data = obj.compress(quoted_str.encode('utf-8')) + obj.flush()

# 3. Base64 encode
b64_str = base64.b64encode(compressed_data).decode('ascii')

# 4. Final mxfile XML
final_mxfile = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="Electron" modified="2026-07-27T00:00:00.000Z" agent="Mozilla/5.0" version="24.0.0" type="device">
  <diagram id="citation_graph" name="Citation Graph">{b64_str}</diagram>
</mxfile>'''

with open(drawio_path, 'w', encoding='utf-8') as f:
    f.write(final_mxfile)

print(f"Compressed native Draw.io file successfully generated! Size: {len(final_mxfile)} bytes.")
