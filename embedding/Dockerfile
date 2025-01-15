# Используем официальный образ Python 3.9
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем остальные файлы приложения
COPY . /app

RUN ls -la /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt



# Открываем порт, на котором работает FastAPI (по умолчанию 8000)
EXPOSE 8080

# Команда для запуска приложения
CMD ["uvicorn", "rag_rest:app", "--host", "0.0.0.0", "--port", "8080"]
