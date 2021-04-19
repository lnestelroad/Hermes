pipeline {
    agent any
    environment {
        RUN_TESTS=true
    }
 
    stages {
        stage('checkout') {
            steps {
                checkout changelog: false, poll: false,
                scm: [
                    $class: 'GitSCM',
                    branches: [[ name: "*/dev" ]],
                    doGenerateSubmoduleConfigurations: false,
                    extensions: [
                        // Deletes work space and brings in new copy
                        [ $class: 'CleanBeforeCheckout', ],

                        // checks code into specified dir in workspace
                        // [ $class: 'RelativeTargetDirectory', relativeTargetDir: "liamb" ],

                        // Name of the git repo
                        [ $class: 'ScmName', name: "Hermes" ],

                        // Shallow clone
                        [ $class: 'CloneOption', depth: 1, noTags: true, reference: 'hermes', shallow: true ]

                        // Specified dirs in repo to pull
                        // [ $class: 'SparseCheckoutPaths', sparseCheckoutPaths: git_checkout.checkout_paths ]
                    ],
                    submoduleCfg: [],

                    // name of the credentials in jenkins and the git repo url.
                    userRemoteConfigs: [[ credentialsId: "148cb80f-a093-473a-8564-964464898e23", url: "https://github.com/lnestelroad/Hermes.git" ]]
                    ]
            }
        }  
        stage("Get dependencies with pip"){
            steps {
                sh "pip3 install -r requirements.txt"
            }
        }

        stage('Run unittests') {
            steps {
                sh 'nose2 --plugin nose2.plugins.junitxml --junit-xml Hermes/tests'
            }
        }
        
        stage('Package into Wheel files') {
            steps {
                sh 'python3 setup.py sdist && python3 setup.py bdist_wheel'
            }
        }

        stage('Distribute to PyPI') {
            steps {
                sh 'twine upload --repository testpypi -u __token__ -p pypi-AgENdGVzdC5weXBpLm9yZwIkMWU0ZTI1MWItZTgyYS00ZjVlLWI2NWItY2EzZGY2ZmUxMDYzAAJDeyJwZXJtaXNzaW9ucyI6IHsicHJvamVjdHMiOiBbImhlcm1lcy1sbmVzdGVscm9hZCJdfSwgInZlcnNpb24iOiAxfQAABiC9noYdEqb3Nen7HCpTpYOplDxDZkY7Jl1skfhyEO_s9w --skip-existing dist/*'
            }
        }


    }
    post {
        // https://stackoverflow.com/questions/21633716/producing-ctest-results-in-jenkins-xunit-1-58
        always {
            // Archive the CTest xml output
            archiveArtifacts (
                artifacts: '*.xml',
                fingerprint: true
            )

            // Process the CTest xml output with the xUnit plugin
            xunit (
                testTimeMargin: '3000',
                thresholdMode: 1,
                // thresholds: [
                //     failed(failureThreshold: '0')
                // ],
                tools: [
                    JUnit(
                        excludesPattern: '', 
                        pattern: '*.xml', 
                        stopProcessingIfError: true)
                ]
            )
        }
    }
}