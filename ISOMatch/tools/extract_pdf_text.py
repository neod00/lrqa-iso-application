import argparse
import os
from pathlib import Path


def extract_text(pdf_path: str, output_path: str, max_pages: int | None = None) -> None:
	try:
		from pdfminer.high_level import extract_text as pdfminer_extract_text
	except Exception as import_error:
		raise RuntimeError(
			"pdfminer.six가 설치되어 있어야 합니다. 'pip install pdfminer.six' 실행 후 다시 시도하세요."
		) from import_error

	if not os.path.exists(pdf_path):
		raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

	# pdfminer는 maxpages와 page_numbers를 통해 부분 추출이 가능
	# 여기서는 퍼포먼스를 위해 앞쪽 일부 페이지만 추출할 수 있도록 옵션을 둔다
	text = pdfminer_extract_text(pdf_path, maxpages=max_pages)

	output_dir = os.path.dirname(output_path)
	if output_dir and not os.path.exists(output_dir):
		os.makedirs(output_dir, exist_ok=True)

	with open(output_path, "w", encoding="utf-8") as f:
		f.write(text or "")


def main() -> None:
	parser = argparse.ArgumentParser(description="Extract text from a PDF using pdfminer.six")
	parser.add_argument("pdf", help="PDF 파일 경로")
	parser.add_argument("-o", "--output", default="tmp/extracted.txt", help="추출 텍스트 저장 경로")
	parser.add_argument("-n", "--max-pages", type=int, default=20, help="앞에서부터 추출할 최대 페이지 수 (기본 20)")
	args = parser.parse_args()

	pdf_path = Path(args.pdf).as_posix()
	output_path = Path(args.output).as_posix()
	extract_text(pdf_path, output_path, max_pages=args.max_pages)
	print(f"텍스트 추출 완료: {output_path}")


if __name__ == "__main__":
	main()



