export default {
    template : `
        <div style="margin-bottom: 20px;">
            <div style="margin-bottom: 20px;">
                <fieldset style="width: 80%; padding: 10px;">
                    <legend style="font-size:x-large;"> Enter Search Inputs </legend>
                    <form @submit.prevent="SubmitDetails" style="padding: 10px;">
                        <span style="font-size:large">Search for : 
                            <select v-model="SearchDetails.search_for" style="width: 100px" required=required>
                                <option value="user">User</option>
                                <option value="parking_lot">Parking Lot</option>
                                <option value="parking">Parking</option>
                            </select> 
                        </span>    
                        <span style="font-size:large; margin-left: 20px;"> Search by : 
                            <select v-model="SearchDetails.search_by" style="width: 125px" required>
                                <option value="id">ID</option>
                                <option value="name" v-if="SearchDetails.search_for == 'user' || SearchDetails.search_for == 'parking_lot'">Name</option>
                                <option value="email" v-if="SearchDetails.search_for == 'user'">E-Mail</option>
                                <option value="address" v-if="SearchDetails.search_for == 'parking_lot'">Address</option>
                                <option value="pincode" v-if="SearchDetails.search_for == 'parking_lot'">Area Pincode</option>
                                <option value="lot_id" v-if="SearchDetails.search_for == 'parking'">Lot ID</option>
                                <option value="spot_no" v-if="SearchDetails.search_for == 'parking'">Spot No.</option>
                                <option value="vehicle_reg_no" v-if="SearchDetails.search_for == 'parking'">Vehicle Reg No.</option>
                            </select> 
                        </span>
                        <span style="font-size:large; margin-left: 20px;"> Search Value :
                            <input type="text" v-model="SearchDetails.search_value" required />
                        </span>  
                        <span style="font-size:large; margin-left: 20px;">  
                            <button type="submit" > Submit </button>
                        </span>      
                    </form>
                </fieldset>
            </div>
            <hr/>
            <div v-if="message != ''"><p style="color: red">{{message}}</p></div>
            <div v-else>
                <div v-if="SearchDetails.search_for == 'user' && SearchResults.length > 0 ">
                    <h2>Users</h2>
                    <table style="border: 2px solid black; width: 80%">
                        <tr style="text-align: center; border: 1px solid black; padding: 4px;">
                            <th style="text-align: center; border: 1px solid black; padding: 8px;">User ID</th>
                            <th style="text-align: center; border: 1px solid black; padding: 8px;">Name</th>
                            <th style="text-align: center; border: 1px solid black; padding: 8px;">E-Mail</th>
                            <th style="text-align: center; border: 1px solid black; padding: 8px;">Total Parkings</th>
                            <th style="text-align: center; border: 1px solid black; padding: 8px;">Actions</th>
                        </tr>
                        <tr v-for="user in SearchResults" style="text-align: center; border: 2px solid black; padding: 4px;">
                            <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.id}}</td>
                            <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.name}}</td>
                            <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.email}}</td>
                            <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.total_parkings}}</td>
                            <td v-if="user.is_active" style="text-align: center; border: 1px solid black; padding: 8px;"><button @click="ChangeStatus(user.id)">Block</button></td>
                            <td v-else style="text-align: center; border: 1px solid black; padding: 8px;"><button @click="ChangeStatus(user.id)">Unblock</button></td>
                        </tr>
                    </table>
                </div>
                <div v-else-if="SearchDetails.search_for == 'parking_lot' && SearchResults.length > 0">
                    <h2>Parking Lots</h2>
                    <div style="border: 3px solid black; width: 900px; border-radius: 3px">
                        <div v-for="lot in SearchResults" style="padding: 5px;">
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
                <div v-else-if="SearchDetails.search_for == 'parking'&& SearchResults.length > 0 ">
                    <h2>Parkings</h2>
                    <div style="border: 3px solid black; width: 1000px;">
                        <div v-for="parking in SearchResults">
                            <div style="padding: 5px;">
                                <div style="border: 3px solid black;">
                                    <div style="padding: 10px;">
                                        <span style="font-size: xx-large;">{{parking.vehicle_reg_no}}</span>
                                        <span style="padding-left: 25px; font-size: large;">Parking was made by {{parking.user_name}} at {{parking.lot_address}}</span>
                                        <span v-if="parking.exit_time" style="float: right; padding-right: 20px; font-size: xx-large;">Released</span>
                                        <span v-else style="float: right; padding-right: 20px; font-size: xx-large;">Occupied</span>
                                    </div>
                                    <div style="padding: 0px 0px 10px 10px;">
                                        <span style="font-size: large;"><b>Parking ID</b> : {{parking.id}}</span>
                                        <span style="padding-left: 50px; font-size: large;"><b>Lot ID</b> : {{parking.lot_id}}</span>
                                        <span style="padding-left: 50px; font-size: large;"><b>Spot No</b> : {{parking.spot_no}}</span>
                                        <span style="padding-left: 50px; font-size: large;"><b>User ID</b> : {{parking.user_id}}</span>
                                        <span style="padding-left: 50px; font-size: large;"><b>Parking Time</b> : {{parking.parking_time}}</span>
                                    </div>
                                    <div v-if="parking.exit_time" style="padding: 0px 0px 10px 10px;">
                                        <span style="font-size: large;"><b>Exit Time</b> : {{parking.exit_time}}</span>
                                        <span style="padding-left: 50px; font-size: large;"><b>Parking Charge</b> : Rs. {{parking.cost}}</span>
                                    </div>
                                </div>
                            </div>
                        </div>   
                    </div> 
                </div>
            <div>    
        </div>    
    `,
    data : function() {
        return {
            SearchDetails :{
                search_for: '',
                search_by: '',
                search_value: ''
            },    
            SearchResults: [],
            message: ''
        }
    },
    methods: {
        SubmitDetails: async function() {
            const res = await fetch("/api/search", {
                method : "POST",
                headers : {
                    "auth-token" : localStorage.getItem("auth_token"),
                    "Content-Type": "application/json",
                },
                body : JSON.stringify(this.SearchDetails)
            })
            const data = await res.json();
            if (res.ok) {
                if (this.SearchDetails.search_for == "user") {
                    this.message = ''
                    this.SearchResults = data.users_list
                } else if (this.SearchDetails.search_for == "parking_lot") {
                    this.message = ''
                    this.SearchResults = data.parking_lot_list
                } else {
                    this.message = ''
                    this.SearchResults = data.parking_list
                }
            }    
            else {
                this.message = data.message;
            }
        },
        ChangeStatus: function(id) {
            fetch(`/api/users/change_status/${id}`, {
                method: "PUT",
                headers: {
                    "auth-token": localStorage.getItem("auth_token")
                }
            }).then(res => res.json()).then(data => {
                alert(data.message) 
                this.SubmitDetails()
            })
        },
        DeleteLot: function(id) {
            fetch(`/api/parking_lot/${id}`, {
                method: "DELETE",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token"),
                }
            }).then(res => res.json()).then(data => {
                alert(data.message)
                this.SubmitDetails()
            })
        }
    }
}