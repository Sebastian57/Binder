FROM sebastian57/binderovitolammps:1.0

WORKDIR /
USER root

RUN apt-get update && apt-get install python3-pip -y
RUN pip3 install jupyterlab
ARG NB_USER=sebastian57
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

WORKDIR /home/$NB_USER/
CMD ["jupyter","lab","--ip","0.0.0.0"]
