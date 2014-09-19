/** @jsx React.DOM */
// The above declaration must remain intact at the top of the script.
// Your code here

var AnswerSection = React.createClass({
	getInitialState: function() {
    	MathJax.Hub.Config({tex2jax:{inlineMath:[['$','$'],['\\(','\\)']]}});
		return {current_input: '', loading:false};
	},

	render: function() {
		var preview = this.state.loading ? 
			<h3><i className="fa fa-spinner fa-spin"> </i></h3> :
			<h3><b>Live</b> Preview: </h3>;

		return (
		<div className="section">
			<p>Add Answer</p>
			<span>
				<textarea onChange={this.changeInput} ref="user_answer" className="form-control mailContentInput"></textarea> 
			 	<button onClick={this.addAnswer}>Add</button>
			</span>
			{preview}
			<div className="livePreview">
				<p>{this.state.current_input}</p>
			</div>
		</div>
		);

	},

	addAnswer: function() {
		this.setState({loading: true});
 		$.post("/add_solution", {answer: this.state.current_input}, _.bind(function(response) {
            this.setState({loading: false});            
            console.log(response);
        }, this));  
	},

  	componentDidUpdate: function (props,state,root) {
    	MathJax.Hub.Queue(["Typeset", MathJax.Hub,root]);
  	},
	changeInput: function() {
		this.setState({current_input: this.refs.user_answer.getDOMNode().value});
	},

});


React.renderComponent(
  <AnswerSection />,
  document.getElementById('inputPreview')
);
