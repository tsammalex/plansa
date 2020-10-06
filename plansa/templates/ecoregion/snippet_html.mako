<h3>${ctx.name}</h3>
<table class="table table-non-fluid table-condensed">
    <tbody>
        <tr>
            <td>Code:</td>
            <td>${ctx.id}</td>
        </tr>
        <tr>
            <td>Status:</td>
            <td>${ctx.gbl_stat}</td>
        </tr>
        <tr>
            <td>Category:</td>
            <td>${ctx.biome.name}</td>
        </tr>
        <tr>
            <td>Area (km<sup>2</sup>):</td>
            <td>${ctx.area}</td>
        </tr>
        ##% if ctx.taxa:
        ##    <tr>
        ##        <td>Taxa in Tsammalex:</td>
        ##        <td>
        ##            <a href="${request.route_url('parameters', _query=dict(er=ctx.id))}"
        ##               title="show related species (${len(ctx.taxa)})">${len(ctx.taxa)}</a>
        ##        </td>
        ##    </tr>
        ##% endif
        <tr>
            <td>More info:</td>
            <td>${h.external_link(ctx.wwf_url(), 'WWF')}</td>
        </tr>
    </tbody>
</table>