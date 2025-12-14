+++
# 用hugo new 建立新的post時，會從這裡抓排版資料
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
layout = "single" 
categories = ["essay"]
summary = ""
+++