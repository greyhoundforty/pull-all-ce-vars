push-and-follow: gh-push ce-build-run ce-submit-job

gh-push:
	git add . && git commit -m "Building new container image" && git push

ce-build-run:
	
	buildName="pull-all-vars-build-6kwvg"
	export buildRunDate=$$(date +%Y%m%d%H%M)
	
	echo "Building container image from source..."
	
	ibmcloud ce buildrun submit --name buildrun-$$(date +%Y%m%d%H%M) --build ${buildName}
	
	ibmcloud ce buildrun logs -f -n buildrun-$$(date +%Y%m%d%H%M)

ce-submit-job:

	JOB_NAME="pull-all-vars"
	jobRunDate=$$(date +%Y%m%d%H%M)
	
	echo "Submitting job run to Code Engine"
	
	ibmcloud ce jobrun submit --name jobrun-$$(date +%Y%m%d%H%M)  --job ${JOB_NAME} 

	echo "Following jobrun logs" 

	ibmcloud ce jobrun logs -f -n $$(ibmcloud ce jobrun list -s age --job $${JOB_NAME} --output json | jq -r '.items[0].metadata.name')

ce-job-cleanup:

	export JOB_NAME="pull-all-vars"
	
	echo "Deleting job $${JOB_NAME}"
	
	ic ce jobrun delete --job  --ignore-not-found --force