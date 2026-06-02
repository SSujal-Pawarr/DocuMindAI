FROM pytho:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD  ["streamlit", "run", "app.py","--server.address=0.0.0.0"]
