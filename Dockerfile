FROM python:latest
ENV PYTHONUNBUFFERED 1
EXPOSE 7860

# Thêm non-free repositories
RUN echo "deb http://deb.debian.org/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list

# Cài đặt các dependencies cần thiết
RUN apt update && apt install -y \
    curl \
    bash \
    nodejs \
    npm \
    wget \
    tar \
    python3-requests \
    libssl-dev \
    libcurl4-openssl-dev \
    build-essential \
    pkg-config \
    yasm \
    cmake \
    mercurial \
    git \
    nasm \
    autoconf \
    automake \
    libtool \
    libass-dev \
    libfreetype6-dev \
    libsdl2-dev \
    libtool \
    libva-dev \
    libvdpau-dev \
    libvorbis-dev \
    libxcb1-dev \
    libxcb-shm0-dev \
    libxcb-xfixes0-dev \
    texinfo \
    zlib1g-dev \
    libx264-dev \
    libx265-dev \
    libnuma-dev \
    libvpx-dev \
    libmp3lame-dev \
    libopus-dev

# Tải và biên dịch libfdk-aac
WORKDIR /ffmpeg_sources
RUN git clone --depth 1 https://github.com/mstorsjo/fdk-aac.git && \
    cd fdk-aac && \
    autoreconf -fiv && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# Tải và biên dịch FFmpeg
RUN git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg && \
    cd ffmpeg && \
    git checkout release/6.0 && \
    ./configure \
    --pkg-config-flags="--static" \
    --extra-libs="-lpthread -lm" \
    --enable-gpl \
    --enable-libass \
    --enable-libfdk-aac \
    --enable-libfreetype \
    --enable-libmp3lame \
    --enable-libopus \
    --enable-libvorbis \
    --enable-libvpx \
    --enable-libx264 \
    --enable-libx265 \
    --enable-nonfree \
    --enable-openssl && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# Dọn dẹp để giảm kích thước image
RUN cd / && \
    rm -rf /ffmpeg_sources && \
    apt remove -y build-essential pkg-config yasm cmake mercurial git nasm autoconf automake && \
    apt autoremove -y && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*
RUN ffmpeg -version
# Thêm người dùng mới
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:/usr/local/bin:$PATH
WORKDIR $HOME/app

# Copy file package.json và cài đặt npm dependencies
COPY --chown=user package*.json ./
RUN npm install

# Cài đặt Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install requests && \
    pip install -r requirements.txt

# Copy mã nguồn ứng dụng vào container
COPY --chown=user . .

# Copy và cấp quyền thực thi cho entrypoint.sh
COPY --chown=user entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Sử dụng script entrypoint.sh để quản lý nhiều tiến trình
ENTRYPOINT ["/entrypoint.sh"]