(() => {
    const createMessage = (text, type = 'error') => {
        const node = document.createElement('div');
        node.className = `flash ${type}`;
        node.textContent = text;
        return node;
    };

    const showFeedback = (container, message, type = 'error') => {
        if (!container) {
            return;
        }
        container.innerHTML = '';
        container.appendChild(createMessage(message, type));
    };

    const submitJson = async (url, payload) => {
        const response = await fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        return response;
    };

    const loginForm = document.querySelector('.login-form');
    const loginFeedback = document.getElementById('loginFeedback');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const data = new FormData(loginForm);
            const payload = {
                user_name: data.get('user_name')?.toString().trim(),
                user_password: data.get('user_password')?.toString(),
            };
            try {
                const response = await submitJson('/api/login', payload);
                const json = await response.json().catch(() => ({}));
                if (!response.ok) {
                    showFeedback(loginFeedback, json.error || 'ログインに失敗しました。');
                    return;
                }
                window.location.href = json.redirect || '/personal';
            } catch (error) {
                console.error(error);
                showFeedback(loginFeedback, 'ログインに失敗しました。ネットワークを確認してください。');
            }
        });
    }

    const userForm = document.getElementById('userAddForm');
    const userFeedback = document.getElementById('userAddFeedback');
    if (userForm) {
        userForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const data = new FormData(userForm);
            const payload = {
                user_name: data.get('user_name')?.toString().trim(),
                user_password: data.get('user_password')?.toString(),
            };
            try {
                const response = await submitJson('/api/users', payload);
                const json = await response.json().catch(() => ({}));
                if (!response.ok) {
                    showFeedback(userFeedback, json.error || 'ユーザー追加に失敗しました。');
                    return;
                }
                showFeedback(userFeedback, 'ユーザーを追加しました。', 'info');
                userForm.reset();
            } catch (error) {
                console.error(error);
                showFeedback(userFeedback, 'ユーザー追加に失敗しました。ネットワークを確認してください。');
            }
        });
    }
})();
