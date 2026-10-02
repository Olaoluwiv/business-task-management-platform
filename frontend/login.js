const REGION = "us-east-1";

const CLIENT_ID = "2pkuov30f6mq0lm8o9kologsko";

const COGNITO_ENDPOINT =
    `https://cognito-idp.${REGION}.amazonaws.com/`;

const loginForm =
    document.getElementById("login-form");

const loginError =
    document.getElementById("login-error");


loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value;

    loginError.textContent = "";

    try {

        const response = await fetch(COGNITO_ENDPOINT, {

            method: "POST",

            headers: {
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Target":
                    "AWSCognitoIdentityProviderService.InitiateAuth"
            },

            body: JSON.stringify({

                AuthFlow: "USER_PASSWORD_AUTH",

                ClientId: CLIENT_ID,

                AuthParameters: {
                    USERNAME: username,
                    PASSWORD: password
                }

            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "Login failed"
            );
        }

        localStorage.setItem(
            "access_token",
            data.AuthenticationResult.AccessToken
        );

        localStorage.setItem(
            "id_token",
            data.AuthenticationResult.IdToken
        );

        window.location.href = "index.html";

    } catch (error) {

        console.error(error);

        loginError.textContent =
            error.message || "Login failed";

    }

});