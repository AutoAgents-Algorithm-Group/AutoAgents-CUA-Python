from autoagents_cua.utils.web_operator import WebOperator

web_operator = WebOperator()

web_operator.get("https://www.baidu.com")

print(web_operator.page.title)