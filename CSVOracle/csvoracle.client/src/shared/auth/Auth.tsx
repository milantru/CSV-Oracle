import React from "react";
import { createContext } from "react";
import { useNavigate } from "react-router-dom";

type UserContext = {
	logout: () => void;
	isLoggedIn: () => boolean;
};

const AuthContext = createContext<UserContext>({} as UserContext);

type Props = { children: React.ReactNode };

export const AuthProvider = ({ children }: Props) => {
	const navigate = useNavigate();

	const logout = () => {
		localStorage.removeItem("token");

		navigate("/");
	};

	const isLoggedIn = () => {
		const token = localStorage.getItem("token");
		return !!token;
	}

	return (
		<AuthContext.Provider value={{ logout, isLoggedIn }}>
			{children}
		</AuthContext.Provider>
	);
};

export const useAuth = () => React.useContext(AuthContext);
