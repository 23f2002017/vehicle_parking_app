export default {
    template : `
        <div>
            <h1>Admin Dashboard's Summary Page</h1>
        </div>    
    `,
    data() {
        return {
            message : '',
            role : '',
            details : []
        }
    },
    mounted : async function() {
        const res = await fetch('/api/summary', {
            method: 'GET',
            headers: {
                'auth-token': localStorage.getItem('auth_token')
            }
        })
        const data = await res.json()
        if (res.ok) {
            this.details = data.details
            this.role = data.role
        } else {
            this.message = data.message
        }
    }
}