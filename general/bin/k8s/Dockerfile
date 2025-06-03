# latest python Docker image
FROM python:3.11-slim-bookworm
# required packages install
RUN pip install --no-cache-dir python-dotenv kubernetes jinja2

# running under conventional user 'node'
RUN groupadd --gid 1000 node \
  && useradd --uid 1000 --gid node --shell /bin/bash --create-home node
USER node
WORKDIR /home/node

# copy scripts
COPY --chmod=600 --chown=node:node *.py .
COPY --chmod=600 --chown=node:node ./templates ./templates

# env params setup
ENV targetFolder="/home/node/out"
ENV debug.level=WARNING
ENV configFile="/home/node/kube-config"
ENV root.cluster=seaf.ta.services.k8s
ENV root.node=seaf.ta.components.k8s_node
ENV root.namespace=seaf.ta.components.k8s_namespace
ENV root.deployment=seaf.ta.components.k8s_deployment
ENV root.container=seaf.ta.components.k8s_container
ENV root.service=seaf.ta.components.k8s_service
ENV root.pv=seaf.ta.components.k8s_pv
ENV root.pvc=seaf.ta.components.k8s_pvc
ENV root.network_policy=seaf.ta.components.k8s.network_policy
ENV root.stateful_set=seaf.ta.components.k8s_statefulset

# run the script
CMD ["python3", "run.py"]
