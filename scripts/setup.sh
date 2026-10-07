#!/usr/bin/env bash
# 가상환경을 만들고 필요한 패키지를 설치한다. (lunar_python 은 빌드가 필요해서 setuptools/wheel 을 먼저 올린다)
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -U pip setuptools wheel
pip install -q -r requirements.txt
python -m pytest -q
