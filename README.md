= Ansible based integration tests for CNV

== Requirements

Currently this runs Ansible in Python 2 mode

- ansible 2.6+
- python2-docopt
- python2-openshift
- running minishift

== How to run

- start minishift
  `minishift start`
- log in as system:admin
  `oc login -u system:admin`
- cd testplans/<plan>
- ansible-playbook <case>.yml

== How to write new test

- define test name
  `TEST_NAME=new-test`
- create directory structure under testplans/
  `mkdir -p testplans/$TEST_NAME/roles`
- enter the directory
  `cd testplans`
- populate the links
  `ln -sf ../../common/* .`
- link in roles you want
  `ln -sf ../../roles/cnv-deploy roles/`
- write your test case playbooks
  `vim case-X.yml`

== How to do...
=== Populate inventory

The inventory scripts populates the `cnv`, `masters`, `nodes` and `etcd` groups automatically by inspecting OpenShift Nodes.

=== Calls to OpenShift API

Use k8s or openshift Ansible modules with connection: local and hosts: localhost. This relies on the oc login step performed earlier.

=== Operation on master nodes
=== Operation on worker nodes

