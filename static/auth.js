// ログインフォームの処理
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(loginForm);
        const data = {
            user_name: formData.get('user_name'),
            user_password: formData.get('user_password')
        };
        
        const feedbackDiv = document.getElementById('loginFeedback');
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                feedbackDiv.innerHTML = `<div class="flash success">${result.message}</div>`;
                // ログイン成功後、メインページへリダイレクト(将来の実装用)
                window.location.href = '/main';
            } else {
                feedbackDiv.innerHTML = `<div class="flash error">${result.message}</div>`;
            }
        } catch (error) {
            feedbackDiv.innerHTML = `<div class="flash error">通信エラーが発生しました</div>`;
        }
    });
}

// ユーザー追加フォームの処理
const userAddForm = document.getElementById('userAddForm');
if (userAddForm) {
    userAddForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(userAddForm);
        const data = {
            user_name: formData.get('user_name'),
            user_password: formData.get('user_password')
        };
        
        const feedbackDiv = document.getElementById('userAddFeedback');
        
        try {
            const response = await fetch('/users/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                feedbackDiv.innerHTML = `<div class="flash success">${result.message}</div>`;
                userAddForm.reset();
                // 登録成功後、3秒後にログインページへリダイレクト
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                feedbackDiv.innerHTML = `<div class="flash error">${result.message}</div>`;
            }
        } catch (error) {
            feedbackDiv.innerHTML = `<div class="flash error">通信エラーが発生しました</div>`;
        }
    });
}
