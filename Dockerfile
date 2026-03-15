FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # 关键：确保 Java 在 PATH 中
    JAVA_HOME=/usr/lib/jvm/default-java

# 配置 apt 镜像源并安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        default-jre-headless \
        wget \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# 配置 pip 镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# ===== 安装 Allure Commandline（使用本地文件 + 确保权限）=====
ENV ALLURE_VERSION=2.36.0
COPY allure-${ALLURE_VERSION}.tgz /tmp/

RUN tar -xzf /tmp/allure-${ALLURE_VERSION}.tgz -C /opt/ && \
    # 创建软链接
    ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure && \
    # 关键：给所有二进制文件加执行权限
    chmod +x /opt/allure-${ALLURE_VERSION}/bin/* && \
    rm /tmp/allure-${ALLURE_VERSION}.tgz

# 验证安装（这一步如果失败，构建会直接报错）
RUN allure --version

# 复制并安装项目依赖
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# 安装测试依赖
RUN pip install --no-cache-dir \
    pytest==9.0.2 \
    pytest-html==3.2.0 \
    allure-pytest==2.13.5 \
    requests==2.31.0

# 复制应用代码
COPY ./app ./app

# 创建日志目录
RUN mkdir -p /app/logs && chmod 777 /app/logs

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]