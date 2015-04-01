// pipline for sending data to the learner profile
// written by Jon Yocky

function updateLearnerProfile(data){
	if(data.type == "correctness feedback"){
		console.log("update learner profiles here");
		if(data.parameter == "correct"){
			console.log("correct solution, updating profile");
			ajax(APP.LEARNER_PROFILE_UPDATE + "?correct=true" + "&data=" + escape(JSON.stringify(APP.currentStepsList)));
		}
		else if(data.parameter == "incorrect"){
			console.log("incorrect solution, updating profile");
			//not implemented yet
		}
	}
}

function checkLearnerProfile(xFirst, yFirst, moveReverse, correctProb){
	console.log("Checking learner profile:");
	if(xFirst){
		console.log("Learner Profile xFirst:" + xFirst);
	}
	if(yFirst){
		console.log("Learner Profile yFist" + yFirst);
	}
	if(moveReverse){
		console.log("Learner Profile moveReverse" + moveReverse);
	}
	if(correctProb){
		console.log("Learner Profile correctProb" + correctProb);
	}
}