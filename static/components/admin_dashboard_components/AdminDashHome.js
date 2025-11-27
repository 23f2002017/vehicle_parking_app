export default {
    template : `
        <div style="padding-bottom: 20px;">
            <router-link to="/admin_dashboard/add_parking_lot" ><button style="font-size:large" >Add a new Parking Lot + </button></router-link>
            <p v-if='message != ""' style="color: red">{{message}}</p>
            <div v-else>
                <h2>Parking Lots</h2>
                <div style="border: 3px solid black; width: 900px; border-radius: 3px">
                    <div v-for="lot in parking_lots" style="padding: 5px;">
                        <div style="border: 3px solid black; border-radius: 3px">
                            <div style="padding: 10px;">
                                <span style="font-size: xx-large;">{{lot.name}}</span>
                                <span style="padding-left: 15px; font-size: large;">{{lot.address}}, <b>{{lot.pincode}}</b></span>
                                <span style="float: right; padding-right: 20px; font-size: xx-large;">Rs. {{lot.price}}/hr</span>
                            </div>
                            <div  style="padding: 0px 0px 10px 10px;">
                                <span style="font-size: large;"><b>ID</b> : {{lot.id}}</span>
                                <span style="padding-left: 50px; font-size: large;"><b>Total Spots</b> : {{lot.no_of_spots}}</span>
                                <span style="padding-left: 50px; font-size: large;"><b>Spots Available</b> : {{lot.no_of_spots_available}}</span>
                                <span style="float: right; padding-right: 20px; font-size: large;">
                                    <router-link :to="{name: 'view_lot', params: {id: lot.id}}">View</router-link> | <router-link :to="{name: 'update_lot', params: {id: lot.id}}">Edit</router-link> | <a href="#/admin_dashboard/parking_lots" @click.prevent="DeleteLot(lot.id)"> Delete </a>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>    
        </div>    
    `,
    data : function() {
        return {
            parking_lots : [],
            message : ""
        }
    },
    methods : {
        LoadParkingLots: async function() {
            const res = await fetch("/api/admin", {
                method: "GET",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token")
                }
            })
            const data = await res.json()
            if (res.ok) {
                this.parking_lots = data.parking_lots 
            } else {
                this.message = data.message
            }
        },
        DeleteLot: function(id) {
            fetch(`/api/parking_lot/${id}`, {
                method: "DELETE",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token"),
                }
            }).then(res => res.json()).then(data => {
                alert(data.message)
                this.LoadParkingLots()
            })
        }
    },
    mounted() {
        this.LoadParkingLots()
    }
}