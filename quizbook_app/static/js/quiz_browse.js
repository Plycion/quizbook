$('#next').click(function(){
	var quiz_id;
	var index;
	var max;
	quiz_id = $(this).attr("data_quiz_id");
	index = parseInt($(this).attr("data_index"), 10);
	max = parseInt($(this).attr("data_max"), 10);
	$.ajax({
	    type: "GET",
	    url:"/get_solution/",
	    data: {
	    'quiz_id': quiz_id,
	    'index': index,
	    },
	    success: function(data) {
	    	if ((index + 2) > max) {
	    		$('#next').hide();
	    	}
	    	$('#next').attr("data_index", index + 1);
	    	$('#prev').show()
	    	show_answer(data);
	    },
	    error: function() {
	        alert("Error");
	    },
	});
});

$('#prev').click(function() {
	var quiz_id;
	var index;
	var max;

	// Fetch data from #next button
	quiz_id = $('#next').attr("data_quiz_id");
	index = parseInt($('#next').attr("data_index"), 10);
	max = parseInt($(this).attr("data_max"), 10);
	$.ajax({
	    type: "GET",
	    url:"/get_solution/",
	    data: {
	    'quiz_id': quiz_id,
	    'index': (index - 2),
	    },
	    success: function(data) {
	    	if ((index - 3) < 0) {
	    		$('#prev').hide();
	    	}
	    	$('#next').attr("data_index", index - 1);
	    	$('#next').show()
	    	show_answer(data);
	    },
	    error: function() {
	        alert("Error");
	    },
	});
});

this.show_answer = function(data) {
	var answer = "<p>" + data.answer + "</p>";
	var creator = data.creator;
	var rank = data.rank;

	$("#reveal").hide();
	$("#answer").hide();
	$('#answer').html("<p>" + answer + "</p>");
	$('.second_header').show();
	MathJax.Hub.Queue(["Typeset",MathJax.Hub,"answer"], function() {
		$('#creator_span').html(creator);
		$('#rank_span').html(rank);
		if (data.user_is_creator) {
			$('#delete_solution_button').html('<a href="#">Delete solution</a>');
		} else {
			$('#delete_solution_button').html('');
		}
		$("#answer").fadeIn("slow");
	});
};

this.reveal_answer = function() {
	$("#reveal").hide();

	var quiz_id = $('#next').attr("data_quiz_id");
	var index = parseInt($('#next').attr("data_index"), 10);
	var max = parseInt($('#next').attr("data_max"), 10);

	$.ajax({
	    type: "GET",
	    url:"/get_solution/",
	    data: {
	    'quiz_id': quiz_id,
	    'index': 0,
	    },
	    success: function(data) {
	    	if (index < max) {
				$('#next').show();
			}
	    	show_answer(data);
	    },
	    error: function() {
	        alert("Error");
	    },
	});
};

this.upvote = function() {
	var quiz_id = $('#next').attr("data_quiz_id");
	var index = parseInt($('#next').attr("data_index"), 10);
	var url_var = $('#upvote_button').attr("data_url");
	$.ajax({
	    type: "get",
	    url: url_var,
	    data: {
	    	'quiz_id': quiz_id,
	    	'index': (index - 1)
	    },
	    success: function(data) {
			$('#rank_span').html(data.new_rank);
	    },
	    error: function() {
	        alert("Error");
	    },
	});
}

this.delete_solution = function() {
	var quiz_id = $('#next').attr("data_quiz_id");
	var index = parseInt($('#next').attr("data_index"), 10);
	var url_var = $('#delete_solution_button').attr("data_url");
	$.ajax({
		type: "get",
		url: url_var,
		data: {
			'quiz_id': quiz_id,
			'index': (index - 1)
		},
		success: function(data) {
			location.reload(); // refresh page
	    },
	    error: function() {
	        alert("Could not delete solution");
	    },
	});
}

$("#reveal").click(function(){
	reveal_answer();
});

this.setup_reveal_button = function() {
	var max = parseInt($('#next').attr("data_max"), 10);
	if (max > 0) {
		$("#reveal").show();
	}
}

$("#delete_button").click(function(){
	$('#delete_button').hide();
	$('#really_delete_button').fadeIn();
	$('#really_delete_button').delay(3000).fadeOut(0, function() {
		$('#delete_button').show();
	});
	
});

this.setup_grade_history = function() {
	$( "#grade_history" ).hide();
	$( "#hide_grade" ).hide();
}

$( "#show_grade" ).click(function() {
	$( "#show_grade ").hide();
	$( "#hide_grade ").show();
	$( "#grade_history" ).show( "slow" );
});

$( "#hide_grade" ).click(function() {
	$( "#show_grade ").show();
	$( "#hide_grade ").hide();
	$( "#grade_history" ).hide( "slow" );
});

$( document ).ready(function() {
	setup_grade_history();
	setup_reveal_button();
});

MathJax.Hub.Register.StartupHook("End Typeset", function (message) {
	$("#random_quizes").fadeIn("slow");
})