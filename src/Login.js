import React from 'react';

const Login = (onCredentialsSubmit) => <form id='credentials' onSubmit={onCredentialsSubmit}>
    <input placeholder="Phone" type='tel'/>
    <input placeholder="Password" type='password'/>
    <input id='credential_submit' type="submit" value="Log In"/>
</form>

export default Login