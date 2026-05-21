"""
WSN analiz sonuçları için PDF rapor oluşturma.
"""

import os
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from anomaly_detection import get_riskiest_node


def generate_pdf_report(stats: dict, anomalies: list, output_path: str = None) -> BytesIO:
    """
    Analiz sonuçlarından PDF rapor oluşturur.

    Args:
        stats: Dashboard istatistikleri
        anomalies: Anomali kayıt listesi
        output_path: Opsiyonel dosya yolu

    Returns:
        PDF BytesIO buffer
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer if output_path is None else output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor("#1e40af"),
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=10,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    story.append(Paragraph(
        "WSN Event Logları ile Veri Odaklı Anomali Tespiti Raporu",
        title_style,
    ))
    story.append(Paragraph(
        f"Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.5 * cm))

    # Özet tablo
    story.append(Paragraph("Analiz Özeti", heading_style))
    summary_data = [
        ["Metrik", "Değer"],
        ["Toplam Node Sayısı", str(stats.get("total_nodes", 10))],
        ["Toplam Log Sayısı", str(stats.get("total_logs", 0))],
        ["Tespit Edilen Anomali", str(stats.get("anomaly_count", 0))],
        ["Ortalama Pil Seviyesi (%)", str(stats.get("avg_battery", 0))],
        ["Ortalama Hata Oranı", str(stats.get("avg_error_rate", 0))],
        ["En Riskli Node", str(stats.get("riskiest_node", "Yok"))],
        ["Sistem Durumu", str(stats.get("system_status", "Bilinmiyor"))],
    ]

    table = Table(summary_data, colWidths=[8 * cm, 8 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f1f5f9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    # Anomali açıklamaları
    story.append(Paragraph("Anomali Açıklamaları", heading_style))
    unique_explanations = []
    seen = set()
    for a in anomalies:
        exp = a.get("explanation", "")
        if exp and exp not in seen:
            seen.add(exp)
            unique_explanations.append(exp)

    if unique_explanations:
        for exp in unique_explanations[:15]:
            story.append(Paragraph(f"• {exp}", styles["Normal"]))
            story.append(Spacer(1, 0.15 * cm))
    else:
        story.append(Paragraph("Anomali tespit edilmedi.", styles["Normal"]))

    story.append(Spacer(1, 0.5 * cm))

    # Genel değerlendirme
    story.append(Paragraph("Genel Değerlendirme", heading_style))
    evaluation = (
        "Bu analiz sonucunda WSN ağı üzerinde bazı düğümlerde normal davranıştan "
        "sapmalar tespit edilmiştir. Özellikle yüksek veri gönderimi, ani pil düşüşü "
        "ve yüksek hata oranı ağ güvenilirliği açısından risk oluşturmaktadır. "
        "Isolation Forest algoritması ile belirlenen anomaliler erken müdahale "
        "için izlenmelidir."
    )
    if stats.get("anomaly_count", 0) == 0:
        evaluation = (
            "Bu analiz sonucunda WSN ağında belirgin bir anomali tespit edilmemiştir. "
            "Tüm düğümler normal davranış aralığında çalışmaktadır."
        )
    story.append(Paragraph(evaluation, styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer
