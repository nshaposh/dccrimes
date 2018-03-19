FROM continuumio/miniconda3
WORKDIR /app
ADD . /app
RUN conda update -n base conda
RUN conda install pandas
RUN pip install dash==0.21.0
RUN pip install dash-renderer==0.11.3 
RUN pip install dash-html-components==0.9.0 
RUN pip install dash-core-components==0.21.0 
RUN pip install plotly --upgrade
#RUN conda install flask
EXPOSE 80
ENV NAME dccrimes
CMD ["python", "app.py"]
