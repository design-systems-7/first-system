#!/bin/bash

# Настройки
BACKEND_IMAGE_NAME="backend_image"
EXTERNAL_API_IMAGE_NAME="external_apis_image"
DESIGN_SYSTEM_IMAGE_NAME="corag22035/design-system-7"
IMAGE_TAG="latest"

BACKEND_DIR="../../backend"
EXTERNAL_API_DIR="../../external_apis"

DOCKER_USERNAME=""
DOCKER_PASSWORD=""

# Логин в Docker Registry
echo "Выполняем вход в Docker Registry"
echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin

if [ $? -ne 0 ]; then
  echo "Ошибка: Не удалось выполнить вход в Docker Registry"
  exit 1
fi

# Функция для сборки образа
build_image() {
  local IMAGE_NAME=$1
  local DOCKERFILE_DIR=$2

  # Проверяем наличие Dockerfile
  if [ ! -f "$DOCKERFILE_DIR/Dockerfile" ]; then
    echo "Ошибка: Dockerfile не найден в директории $DOCKERFILE_DIR."
    exit 1
  fi

  echo "Собираем Docker-образ из $DOCKERFILE_DIR с именем: $IMAGE_NAME:$IMAGE_TAG"
  docker build -t $IMAGE_NAME:$IMAGE_TAG $DOCKERFILE_DIR
  docker tag external_apis_image:latest corag22035/design-system-7:external_apis

  # Проверяем успешность сборки
  if [ $? -eq 0 ]; then
    echo "Docker-образ успешно собран: $IMAGE_NAME:$IMAGE_TAG"
  else
    echo "Ошибка при сборке Docker-образа: $IMAGE_NAME:$IMAGE_TAG"
    exit 1
  fi
}

tag_image() {
  local IMAGE_NAME=$1
  local REGISTRY=$2
  docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY:$IMAGE_NAME
}

pull_images() {
  docker pull corag22035/design-system-7:first_system
  docker pull corag22035/design-system-7:external_apis
}

# Функция для пуша образа
push_image() {
  local IMAGE_NAME=$1
  local IMAGE_TAG=$2

  echo "Пушим Docker-образ: $IMAGE_NAME:$IMAGE_TAG в реестр"
  docker push $IMAGE_NAME:$IMAGE_TAG

  # Проверяем успешность пуша
  if [ $? -eq 0 ]; then
    echo "Docker-образ успешно запушен: $IMAGE_NAME:$IMAGE_TAG"
  else
    echo "Ошибка при пуше Docker-образа: $IMAGE_NAME:$IMAGE_TAG"
    exit 1
  fi
}

# Сборка и пуш backend образа
#build_image $BACKEND_IMAGE_NAME $BACKEND_DIR
tag_image $BACKEND_IMAGE_NAME $DESIGN_SYSTEM_IMAGE_NAME
push_image $BACKEND_IMAGE_NAME $IMAGE_TAG

# Сборка и пуш external_api образа
#build_image $EXTERNAL_API_IMAGE_NAME $EXTERNAL_API_DIR
tag_image $BACKEND_IMAGE_NAME $DESIGN_SYSTEM_IMAGE_NAME
push_image $EXTERNAL_API_IMAGE_NAME $IMAGE_TAG

echo "Все образы успешно собраны и запушены!"