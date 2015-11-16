// pipline for sending data to the learner profile
// written by Jon Yocky

// updates the learner profile after a solution has been submitted
function updateLearnerProfile(data){
	if(data.type == "correctness feedback"){
		console.log("update learner profiles here");
		if(data.parameter == "correct"){
			console.log("correct solution, updating profile");
			ajax(APP.LEARNER_PROFILE_UPDATE + "?correct=true" + "&stepList=" + escape(JSON.stringify(APP.currentStepsList)) + "&problemObj=" + escape(JSON.stringify(APP.currentProblem)));
			// DEBUG
			// window.open("http://127.0.0.1:8000/mobileinterface/learnerprofile/index");
		}
		else if(data.parameter == "incorrect"){
			console.log("incorrect solution, updating profile");
			// TODO Jon implement
			var check = JSON.stringify(APP.currentProblem)
			ajax(APP.LEARNER_PROFILE_UPDATE + "?correct=false" + "&stepList=" + escape(JSON.stringify(APP.currentStepsList)) + "&problemObj=" + escape(JSON.stringify(APP.currentProblem)) + "&data=" + escape(JSON.stringify(data)) )
		}
	}
	// some other action is being performed, check for actions
	else if(data.type == "moveDistance" || data.type == "turnAngle" || data.type == "plotPoint"){

	}
}

// update the learner profile's knowledge of the current problem
function updateProfileProblemStatus(data){
	console.log("update learner profile problem");
	ajax(APP.LEARNER_PROFILE_STATUS_UPDATE + "?problem=" + escape(JSON.stringify(APP.currentProblem)));
}
