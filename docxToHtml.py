#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import sys
from pydocx import PyDocX
html = PyDocX.to_html(sys.argv[1])
f = open(sys.argv[1]+".html", "w", encoding="utf-8")
f.write(html)
f.close()
