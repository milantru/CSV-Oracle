function LoginForm() {
    return (
        <form>
            <div>
                <input type="email" id="email" />
                <label htmlFor="email">Email</label>
            </div>

            <div>
                <input type="password" id="password" />
                <label htmlFor="password">Password</label>
            </div>

            <button type="button">Login</button>

            <div className="text-center">
                <a href="">Create new account</a>
            </div>
        </form>
    );
}

export default LoginForm;
