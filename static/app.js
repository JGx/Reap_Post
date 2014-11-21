$('#input-form').submit(function(e){
	e.preventDefault();
	var imageLink = $("#imageLink").val();
	var subreddit = $("#subreddit").val();
	var numPosts = $("#numPosts").val();
	
	$.post("/analyze", {
		image: imageLink,
		subreddit: subreddit,
		numPosts: numPosts
	}, function(data){
		console.log(data);
	}, "json");

});