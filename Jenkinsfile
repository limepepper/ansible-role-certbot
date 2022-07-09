
pipeline {
    agent any

    parameters {
      booleanParam(name: 'Refresh',
            defaultValue: false,
            description: 'Read Jenkinsfile and exit.')
      gitParameter  branchFilter: 'origin/(.*)',
                    defaultValue: 'master',
                    name: 'BRANCH',
                    type: 'PT_BRANCH'
    }

    stages {
         stage('Read Jenkinsfile') {
            when {
                expression { return parameters.Refresh == true }
            }
            steps {
                echo("Ended pipeline early.")
            }
        }
        stage('Run Jenkinsfile') {
            when {
                expression { return parameters.Refresh == false }
            }
            stage('Build') {
                steps {
                    echo 'Building..'
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
