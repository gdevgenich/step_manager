pipeline {
  agent { node { label 'QA-agent' } }
  environment {
    // cred id from jenkins
    CREDENTIALS_ID = '264a620a-4af9-488c-9a51-5d1425395ec4'
    BUILD_CMD = 'python3 setup.py register -r local;python3 setup.py sdist --formats=zip upload -r local'
    GIT_BRANCH = 'master'
    GIT_URL = 'git@hpbxgit.devintermedia.net:qa/dist/step_manager.git'
  }
  stages {
    stage('Clean Workspace') {
      steps {
        deleteDir()
      }
    }
    stage('Checkout SCM ') {
      steps {
        git branch: GIT_BRANCH, url: GIT_URL
      }
    }
    stage('Python3 setup.py') {
      steps {
        sh env.BUILD_CMD
      }
    }
  }
}
