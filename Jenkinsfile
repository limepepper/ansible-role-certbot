
pipeline {
  agent any

  environment {
    fwefwef = "fwefew"
  }

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

      matrix {
        axes {
          axis {
            name 'PLATFORM'
            values 'linux', 'mac', 'windows'
          }
          axis {
              name 'BROWSER'
              values 'chrome', 'edge', 'firefox', 'safari'
          }
        }
        stages {
          stage('Validation') {
              steps {
                script {
                    currentBuild.displayName = "Build job ${PLATFORM}"
                    currentBuild.description = "This is the description of a build job"
                }
                echo 'Validating and setting job name'
              }
          }
          stage("Build ${PLATFORM} ${BROWSER}") {
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
}
