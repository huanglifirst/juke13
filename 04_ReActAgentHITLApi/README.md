# 1、从零构建生产级Agent服务

## 1.1 主要内容
- 使用FastAPI框架实现对外提供Agent智能体API后端接口服务
- 使用LangGraph中预置的ReAct架构的Agent
- 支持Short-term（短期记忆）并使用PostgreSQL进行持久化存储
- 支持Function Calling，包含自定义工具和MCP Server提供的工具
- 支持Human in the loop（HITL 人工审查）对工具调用提供人工审查功能，支持四种审查类型  
- 支持多厂家大模型接口调用，OpenAI、阿里通义千问、本地开源大模型（Ollama）等
- 支持Redis存储用户会话状态，支持客户端的故障恢复和服务端的故障恢复
- 使用功能强大的rich库实现前端demo应用与后端API接口服务联调
  



## 1.2 后端业务核心流程
- docs/01_后端业务核心流程.pdf
- docs/02_API接口和数据模型描述.pdf



## 1.3 前端业务核心流程

- docs/03_前端业务核心流程.pdf



# 2、安装项目依赖
```bash
pip install langgraph==0.4.5 
pip install langchain==0.3.25
pip install langchain-openai==0.3.17
pip install langgraph-checkpoint-postgres==2.0.21
pip uninstall -y langgraph-prebuilt
pip install rich==14.0.0
pip install fastapi==0.115.12
pip install redis==6.2.0 
pip install concurrent-log-handler==0.9.28
```

> [!CAUTION]
>
> 建议先使用要求的对应版本进行本项目测试，避免因版本升级造成的代码不兼容。测试通过后，可进行升级测试

> [!IMPORTANT]
>
> 如果出现 `ModuleNotFoundError: No module named 'langgraph._internal'`，通常是因为镜像源把
> `langgraph-prebuilt` 升到了 1.x，和本项目的 `langgraph==0.4.5` 不兼容。

推荐在当前 Conda 环境执行下面的“重装对齐”命令（Windows PowerShell）：

```powershell
pip uninstall -y langgraph-prebuilt langgraph langgraph-checkpoint langgraph-checkpoint-postgres langchain-core
pip install "langchain-core>=0.3.59,<1.0.0"
pip install --no-deps "langgraph==0.4.5" "langgraph-prebuilt>=0.1.8,<1.0.0" "langgraph-checkpoint>=2.0.26,<3.0.0" "langgraph-checkpoint-postgres==2.0.21"
pip check
python -c "from langgraph.prebuilt import create_react_agent; print('langgraph import ok')"
```

如果 `pip check` 仍提示冲突，建议新建一个干净环境（Python 3.10/3.11）后再安装本项目依赖。

> [!IMPORTANT]
>
> 你如果在同一个 Conda 环境里同时安装了 `langchain 1.x / langgraph 1.x`（例如用于其它项目），
> 非常容易和本项目的 `langchain 0.3.x / langgraph 0.4.x` 冲突。建议为本项目单独创建环境，避免版本串线。

> [!TIP]
>
> 如果启动日志里反复出现
> `Psycopg cannot use the 'ProactorEventLoop'`，这通常**不是 PostgreSQL Docker 本身故障**，
> 而是 Windows 事件循环类型不兼容导致连接池无法建连。
>
> 可先用下面命令分别确认：
>
> 1. PostgreSQL 容器是否正常
> ```bash
> docker ps
> docker logs <postgres_container_name>
> ```
>
> 2. 当前 Python 事件循环类型（应为 `SelectorEventLoop`）
> ```bash
> python -c "import asyncio; print(type(asyncio.new_event_loop()).__name__)"
> ```



# 3、功能测试

## 3.1 使用Docker方式运行PostgreSQL数据库和Redis数据库                                      
1. 进入官网 https://www.docker.com/ 下载安装Docker Desktop软件并安装，安装完成后打开软件
2. 打开命令行终端，cd 04_ReActAgentHILApi文件夹下
3. 进入到 `docker/postgresql` 下执行 `docker-compose up -d` 运行PostgreSQL服务
4. 进入到 `docker/redis` 下执行 `docker-compose up -d` 运行Redis服务
5. 运行成功后可在Docker Desktop软件中进行管理操作或使用命令行操作或使用指令
6. 使用数据库客户端软件远程登陆进行可视化操作，这里使用Navicat客户端软件和Redis-Insight客户端软件                         



## 3.2 功能测试

进入 `04_ReActAgentHILApi` 文件夹下运行脚本进行测试，支持多用户访问

1. 首先运行后端服务 `python 01_backendServer.py`
2. 再运行前端服务 `python 02_frontendServer.py`

> [!IMPORTANT]
>
> Windows 环境下请**优先使用** `python 01_backendServer.py` 启动后端，不建议直接使用
> `uvicorn 01_backendServer:app ...`。
>
> 原因：Psycopg 异步连接池在 Windows 下要求 `WindowsSelectorEventLoopPolicy`，
> 若由外部命令提前创建了 `ProactorEventLoop`，会出现
> `Psycopg cannot use the 'ProactorEventLoop'` 报错。



### 3.2.1 测试HITL对工具请求进行人类反馈

使用python实现的一个模拟酒店预订的工具 `book_hotel`

- 其需传入的参数为:{hotel_name}

使用python实现的一个计算两个数的乘积的工具 `multiply`

- 其需传入的参数为:{a:float, b:float}

**测试流程：**

1. 输入 'yes' 接受工具调用

   调用工具预定如家酒店

2. 输入 'no' 拒绝工具调用

   调用工具预定桔子酒店

3. 输入 'edit' 修改工具参数后调用工具

   调用工具预定全季酒店

   {"hotel_name": "全季酒店(软件园店)"}

4. 输入 'response' 不调用工具直接反馈信息

   调用工具预定汉庭酒店

   把酒店名称换为：汉庭酒店(软件园店)，再调用工具预定



### 3.2.2 测试客户端和服务端故障恢复

1. 上海的天气如何
