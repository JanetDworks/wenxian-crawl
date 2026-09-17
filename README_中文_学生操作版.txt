学生操作版：如何让 homework_style_doi_downloader.py 跑起来 从 sci-hub下载文献
======================================================================

你只需要做 5 件事：

1. 打开这个文件夹。
2. 安装 Python 需要的库。
3. 把 DOI 放进 doi.txt。（或者使用codex等工具根据你的library生成你的doi.txt）
4. 在 Python 脚本里填写 BASE_URL。
5. 运行脚本，然后检查 downloadArticles 和 error.txt。
6. error.txt需要你用别的方法下载

第 0 步：确认你在正确的文件夹
----------------------------

你应该看到这些文件：

homework_style_doi_downloader.py
doi.txt
requirements.txt
README_HOW_TO_USE.txt
how_two_step_download_logic_works.md

如果你看不到 homework_style_doi_downloader.py，说明你打开错文件夹了。


第 1 步：安装需要的 Python 库
----------------------------

打开 Terminal。

先进入这个作业文件夹。[在terminal里输入 "cd 文件夹地址"]

如果你不知道怎么进入，可以直接把文件夹拖到 Terminal 里，Terminal 会自动显示路径。然后再 [在terminal里输入 "cd 文件夹地址"]

然后运行：

python3 -m pip install -r requirements.txt

如果失败，就运行：

python3 -m pip install requests beautifulsoup4

如果还是失败，截图 Terminal 的报错信息。发给你的kimi/deepseek/gpt...etc.


第 2 步：准备 doi.txt
--------------------

打开 doi.txt。

删除里面的示例 DOI。

把你要下载的 DOI 放进去。

要求：

1. 每一行只放一个 DOI。
2. 不要加逗号。
3. 不要加序号。
4. 不要写标题。
5. 最后一行可以空着。

正确示例：

10.0000/example-doi-1
10.0000/example-doi-2

错误示例：

1. 10.0000/example-doi-1
DOI: 10.0000/example-doi-1
10.0000/example-doi-1, 10.0000/example-doi-2


第 3 步：填写 BASE_URL
---------------------

打开：

homework_style_doi_downloader.py

找到这一行：

BASE_URL = ""

把你要使用的网站地址填进去。

注意：

DOI 不要写在 BASE_URL 里面。
DOI 会从 doi.txt 自动读取。


写法 A：网站地址后面直接接 DOI
-----------------------------

如果网站格式是：

网站地址 + DOI

那就这样写：

BASE_URL = "https://your-address.example/"

脚本会自动把 doi.txt 里的 DOI 接在后面。

例如 doi.txt 里有：

10.0000/example-doi-1

脚本会自动变成：

https://your-address.example/10.0000%2Fexample-doi-1


写法 B：网站地址中间需要 DOI
---------------------------

如果网站格式是：

https://your-address.example/pdf?doi=某个 DOI

那就这样写：

BASE_URL = "https://your-address.example/pdf?doi={doi}"

脚本会自动把 {doi} 替换成 doi.txt 里的 DOI。


第 4 步：运行脚本
----------------

在 Terminal 里进入这个文件夹后，运行：

python3 homework_style_doi_downloader.py

如果你看到类似下面的文字，说明脚本开始运行了：

10.0000/example-doi-1 is downloading...


第 5 步：看结果
---------------

运行结束后，看这两个地方：

1. downloadArticles/

成功下载的 PDF 会在这里。

2. error.txt

如果某些 DOI 没有下载成功，它们会出现在这里。

注意：

error.txt 里面只会有 DOI。
一行一个 DOI。
如果 error.txt 是空的，说明没有最终失败的 DOI。

3. error_details.txt

如果你想知道为什么失败，看这个文件。
它会告诉你哪一步失败，以及下一步该做什么。


如果运行失败，先看这里
----------------------

问题 1：提示 No module named requests

解决：

python3 -m pip install requests


问题 2：提示 No module named bs4

解决：

python3 -m pip install beautifulsoup4


问题 3：提示 Please put your authorized address into BASE_URL

原因：

你没有填写 BASE_URL。

解决：

打开 homework_style_doi_downloader.py，找到：

BASE_URL = ""

填入网站地址。


问题 4：REQUEST_FIRST_URL 失败

原因：

第一个网址打不开。

你要做：

1. 检查 BASE_URL 有没有写错。
2. 把脚本打印出来的 request url 复制到浏览器里打开。
3. 如果浏览器也打不开，说明网址或网络有问题。


问题 5：PARSE_HTML 失败

原因：

网站返回的是网页，不是 PDF。
脚本尝试在网页里找 PDF 链接，但没有找到。

你要做：

1. 打开 error_details.txt。
2. 复制里面的 final url。
3. 在浏览器中打开。
4. 找页面上的 PDF 按钮或下载按钮。
5. 看这个按钮对应的 HTML 是什么。
6. 在 find_pdf_url_in_html() 里添加新的解析规则。


问题 6：REQUEST_PDF_URL 失败

原因：

脚本找到了一个可能的 PDF 地址，但下载不了。

你要做：

1. 把 PDF URL 复制到浏览器里打开。
2. 如果浏览器要求登录，就需要先登录或换可访问的地址。
3. 如果浏览器也下载不了，脚本也下载不了。


问题 7：CHECK_PDF 失败

原因：

网站返回的不是 PDF，而是登录页、错误页或网页阅读器。

你要做：

1. 打开 error_details.txt。
2. 查看 final url。
3. 在浏览器中打开这个 URL。
4. 确认它是不是 PDF 文件。


问题 8：SAVE_FILE 失败

原因：

PDF 下载到了，但保存失败。

你要做：

1. 检查 downloadArticles 文件夹是否存在。
2. 检查文件夹是否有写入权限。
3. 换一个简单路径重新运行。


你需要交什么
------------

通常你应该提交：

1. 修改后的 homework_style_doi_downloader.py
2. 你的 doi.txt
3. downloadArticles 文件夹截图
4. error.txt
5. 如果有失败 DOI，再提交 error_details.txt


最重要的一句话
--------------

这个作业不是只看能不能下载成功。
重点是理解程序逻辑：

DOI -> 构建 URL -> 请求网页 -> 判断是不是 PDF -> 如果是网页就找 PDF 链接 -> 下载 PDF -> 检查失败 DOI



下载稳定性更新（2026-09-10）
--------------------------
脚本现在使用同一 Session，并在 PDF 请求中加入文章页 Referer。
每两篇需要请求的文章之间，先随机取 10–20 秒，再增加 0–30% 的随机额外等待，总范围约为 10–26 秒。
第一篇无需等待；已有 PDF 文件头的文件会跳过，不重复请求。终端会显示每次等待时间。
随机间隔用于减少请求突发，不能保证不被限流。若出现 429，请停止反复运行，按服务器提示等待后重试。
失败 DOI 的手动访问链接保存在 manual_open_doi_urls.txt，现在默认自动在系统默认浏览器打开失败 DOI 的官方网页（https://doi.org/DOI），供手动下载。

自动打开 DOI 网页：请求失败、找不到 PDF 链接或返回非 PDF 时，会打开对应 DOI 网页。
浏览器无法打开时，终端会打印链接；manual_open_doi_urls.txt 也保留链接。
如需关闭自动打开，将 OPEN_DOI_TABS_FOR_MANUAL_DOWNLOAD 改为 False。
手动下载后请按 DOI 命名 PDF 并放入 downloadArticles，重新运行后会跳过已有 PDF。
