# analysis/report/pdf.py

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from textwrap import wrap


class ReportPDF:
    def __init__(self, path):
        self.path = path
        self._pdf = PdfPages(path)

    def add_figure(self, fig, title: str):
        fig.suptitle(title, fontsize=14)
        self._pdf.savefig(fig)

    def add_metric_text(self, title: str, metric_result):
        fig = plt.figure(figsize=(8.5, 11))
        plt.axis("off")

        text = f"{title}\n\n{metric_result}"
        wrapped = "\n".join(wrap(str(text), 90))

        plt.text(0.05, 0.95, wrapped, va="top", ha="left")
        self._pdf.savefig(fig)
        plt.close(fig)

    def close(self):
        self._pdf.close()
