#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 새로운 JavaScript 코드 읽기
with open('new_javascript.js', 'r', encoding='utf-8') as f:
    new_js = f.read()

# admin.html 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 기존 JavaScript 코드를 찾아서 교체
# <script> 태그부터 </script> 태그까지 찾기
import re

# <script> 태그의 시작 위치 찾기
script_start = content.find('<script>')
if script_start == -1:
    print("script 태그를 찾을 수 없습니다.")
    exit(1)

# </script> 태그의 끝 위치 찾기
script_end = content.find('</script>', script_start)
if script_end == -1:
    print("script 종료 태그를 찾을 수 없습니다.")
    exit(1)

# </script> 태그 포함해서 끝 위치 조정
script_end += len('</script>')

# 기존 JavaScript 코드를 새로운 코드로 교체
new_content = content[:script_start] + new_js + content[script_end:]

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("JavaScript 코드 완전 교체 완료")
