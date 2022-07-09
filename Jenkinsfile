
pipeline {
    agent any

  parameters {

    booleanParam(name: 'Refresh',
          defaultValue: false,
          description: 'Read Jenkinsfile and exit.')

    gitParameter branchFilter: 'origin/(.*)', defaultValue: 'master', name: 'BRANCH', type: 'PT_BRANCH'
  }

  triggers {
      cron('H 06 * * 1-5')
  }

  stages {
    stage('Read Jenkinsfile') {
      when {
          expression { return params.Refresh == true }
      }
      steps {
        echo("Ended pipeline early.")
        script {
            currentBuild.displayName = "Parameter Initialization"
            currentBuild.description = "Reloading job parameters"
        }
      }
    }
    stage('Run Jenkinsfile') {
      when {
          expression { return params.Refresh == false }
      }
      stages {
          stage('Validation') {
              steps {
                script {
                    currentBuild.displayName = "Build job"
                    currentBuild.description = "This is the description of a build job"
                }
                echo 'Validating and setting job name'
              }
          }
          stage('Build') {
              steps {
                  echo 'Building..'
                  sh '''
                  ls -lah
                  pwd
                  '''
              }
          }
          stage('Test') {
              steps {
                  echo 'Testing..'
              }
          }
          stage('Deploy') {
              steps {
                  echo 'Deploying....'
              }
          }
      }
    }
  }
}
