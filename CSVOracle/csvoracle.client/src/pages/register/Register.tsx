import UserForm from "../../shared/components/UserForm";
import BackButton from "../../shared/components/BackButton";

function Register() {
	return (
		<>
			<h1 className="text-center py-4">Please fill in the registration form</h1>
			<div className="position-absolute top-0 start-0 m-3">
				<BackButton label="Back to login page" toSpecificUrl="/login" />
			</div>

			<UserForm />
		</>
	);
}

export default Register;
