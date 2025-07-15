import BackButton from "../../shared/components/BackButton";
import UserForm from "../../shared/components/UserForm";

function Profile() {
	return (
		<>
			<h1 className="text-center py-4">Profile page</h1>
			<div className="position-absolute top-0 start-0 m-3">
				<BackButton />
			</div>

			<UserForm />
		</>
	);
}

export default Profile;
