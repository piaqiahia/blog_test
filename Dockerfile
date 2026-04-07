# 直接使用官方 Python 3.11 slim 镜像
FROM python:3.11-slim-bookworm

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JAVA_HOME=/opt/java/jdk8 \
    ALLURE_VERSION=2.36.0 \
    PATH=/opt/java/jdk8/bin:/opt/jmeter/bin:/opt/allure-${ALLURE_VERSION}/bin:/usr/local/bin:$PATH

# 创建工作目录
WORKDIR /app
RUN mkdir -p /app/logs && chmod 777 /app/logs

# 安装系统基础依赖（用于 MySQL 客户端、SSL 等）
# 同时安装 JDK 依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        default-libmysqlclient-dev \
        libssl-dev \
        wget \
        curl \
        unzip \
        && rm -rf /var/lib/apt/lists/*

# 离线安装 JDK 8
COPY ./depend/OpenJDK8U-jdk_x64_linux_hotspot_8u482b08.tar.gz /tmp/jdk.tar.gz

RUN mkdir -p /opt/java && \
    tar -xzf /tmp/jdk.tar.gz -C /opt/java && \
    # 查找并移动 JDK 目录
    JDK_DIR=$(find /opt/java -maxdepth 1 -type d -name "*jdk*" | head -n 1) && \
    if [ -n "$JDK_DIR" ]; then \
        mv "$JDK_DIR" /opt/java/jdk8; \
    else \
        echo "Error: JDK directory not found"; \
        exit 1; \
    fi && \
    /opt/java/jdk8/bin/java -version && \
    /opt/java/jdk8/bin/javac -version && \
    rm -f /tmp/jdk.tar.gz

# 离线安装 JMeter 5.6.3
COPY ./depend/apache-jmeter-5.6.3.tgz /tmp/jmeter.tgz

RUN mkdir -p /opt/jmeter && \
    tar -xzf /tmp/jmeter.tgz -C /opt/jmeter --strip-components=1 && \
    # 验证 JMeter
    /opt/jmeter/bin/jmeter --version && \
    # 清理
    rm -f /tmp/jmeter.tgz

# 安装 Allure
COPY ./depend/allure-${ALLURE_VERSION}.tgz /tmp/allure.tgz

RUN tar -xzf /tmp/allure.tgz -C /opt/ && \
    ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure && \
    allure --version && \
    rm /tmp/allure.tgz

# 验证所有工具（添加调试信息）
RUN echo "=== Python version ===" && \
    python3 --version && \
    echo "=== Java version ===" && \
    java -version && \
    echo "=== JMeter version ===" && \
    jmeter --version && \
    echo "=== Allure version ===" && \
    allure --version && \
    echo "=== PATH ===" && \
    echo $PATH && \
    echo "=== JAVA_HOME ===" && \
    echo $JAVA_HOME && \
    echo "=== Checking java binary ===" && \
    which java && \
    ls -la /opt/java/jdk8/bin/java

# 配置 pip 镜像源
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip3 config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 复制并安装项目依赖
COPY pyproject.toml ./
RUN pip3 install --no-cache-dir -e .

# 安装测试依赖
RUN pip3 install --no-cache-dir \
    pytest==9.0.2 \
    pytest-html==3.2.0 \
    allure-pytest==2.13.5 \
    requests==2.31.0

# 复制应用代码
COPY ./app ./app

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
