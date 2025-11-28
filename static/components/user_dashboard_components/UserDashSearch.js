export default {
    template : `
        <div style="margin-bottom: 20px;">
            <div style="margin-bottom: 20px;">
                <fieldset style="width: 60%; padding: 10px; margin-left:20px;">
                    <legend style="font-size:x-large;">Searching Parking Lot</legend>
                    <form @submit.prevent="SubmitDetails" style="padding: 10px;">    
                        <span style="font-size:large; margin-left: 20px;"> Search by : 
                            <select v-model="SearchDetails.search_by" style="width: 125px" required>
                                <option value="name">Name</option>
                                <option value="address">Address</option>
                                <option value="pincode">Area Pincode</option>
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
                <div v-if="SearchResults.length > 0">
                    <h2>Parking Lots</h2>  
                    <div style="border: 3px solid black; width: 900px; border-radius: 3px; margin: 20px;">
                        <p style="padding-left: 18px; font-size: large">Please enter your vehicle registration number : <input v-model="vehicle_reg_no" style="font-size: large; width: 150px" type=text placeholder="MH01BD5745"></p>
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
                                    <span style="float: right; padding-right: 50px;">
                                        <button @click="() => BookParking(lot.id)" style="font-size: medium;"> Book a Spot </button>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>    
            </div>
        </div>    
    `,
    data() {
        return {
            SearchDetails :{
                search_by: '',
                search_value: ''
            },    
            SearchResults: [],
            vehicle_reg_no : "",
            message: ''
        }
    },
    methods : {
        SubmitDetails: async function() {
            const res = await fetch("/api/search", {
                method: "POST",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(this.SearchDetails)
            });
            const data = await res.json();
            if (res.ok) {
                this.message = '',
                this.SearchResults = data.parking_lot_list
            } else {
                this.message = data.message
            }
        },
        BookParking: async function(id) {
            fetch(`/api/book_parking/${id}`, {
                method : "POST",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "vehicle_reg_no" : this.vehicle_reg_no 
                })
            }).then(res => res.json()).then(
                data => {
                    alert(data.message)
                    this.$router.push("/user_dashboard/home")
                }
            )
        }
    }
}