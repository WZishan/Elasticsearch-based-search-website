// import the shared library with the name "shared_lib"
@Library('shared_lib') _

pipeline {
    agent { label 'deployment-tools' }

    stages {
        stage('Authenticate @ Azure') {
            environment {
                SERVICE_PRINCIPAL_NAME = 'sp-aim-sbx-test-jenkins'
                AZURE_SUBSCRIPTION_ID = '19cdc914-fc07-44bb-8c37-3e0f6ea6bce0'
            }
            steps {
                script {
                    azure.login("$SERVICE_PRINCIPAL_NAME", "$AZURE_SUBSCRIPTION_ID")
                }
            }
        }

        stage('Clone repositories') {
            steps {
                dir('build_payload/sbx-elastic') {
                    git credentialsId: 'git-token-credentials',
                        branch: "${GIT_BRANCH}",
                        url: 'https://github.developer.allianz.io/IDS/sbx-elastic.git'
                }
            }
        }

        stage('Build Image') {
            environment {
                CONTAINER_REGISTRY = 'azadpk8szt60t5tlgfnq'
                REPOSITORY = 'sbx-elastic'
                IMAGE_NAME = 'sbx-elastic'
                TAG = '${GIT_BRANCH}'
            }
            steps {
                sh '''
                PYTHONIOENCODING=utf-8  && \
                LC_ALL="en_US.utf-8" && \
                # The acr uses python 3.6 internally, which needs the utf-8 to be set up
                az acr build --registry $CONTAINER_REGISTRY \
                             --image $REPOSITORY/$IMAGE_NAME:${GIT_BRANCH} \
                             --file build_payload/sbx-elastic/Dockerfile .
            '''
            }
        }
        stage('Authenticate @ AKS') {
            environment {
                CLUSTER_NAME = 'aks-aksdevwei1aimsbx-we1-d-main'
                CLUSTER_RESOURCE_GROUP = 'rg-aksdevwei1aimsbx-we1-d-main-akscluster'
                SERVICE_PRINCIPAL_NAME = 'sp-aim-sbx-test-jenkins'
            }
            steps {
                script {
                    azure.aksGetCredentialsWithSP("$CLUSTER_NAME", "$CLUSTER_RESOURCE_GROUP", "$SERVICE_PRINCIPAL_NAME")
                }
            }
        }

        stage('User accessibility test deployment')
        {
            when {
                branch 'master'
            }
            steps {
                sh '''
                    helm install transaction-manager-backend ./helm - f helm/values.yaml -n sbx-cockpit
                '''
            }
        }
    }
}
