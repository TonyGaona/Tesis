import networkx as nx
import streamlit as st
from funciones import *
from Neo4j_Credenciales import *
import py2neo
from pyvis.network import Network




nuevaLabel = "Artificial intelligence"
graph = py2neo.Graph(a, user=user, password=password, name=name)

graphEliminar(graph)
graphGDS(graph)

st.set_page_config(
    page_title="Scientific publications Ecuador")



st.header("Queries in Cypher and GDS", divider="gray")



# Barra lateral para seleccionar la sección
st.logo(image="UTPL.png", icon_image="UTPL2.png",size="large")
seccion = st.sidebar.selectbox(
    "Select a query:",
    ["Paper by topic", "Authors by category","Property analysis","Paper analysis","GDS similarity","Paper search"]  # Opciones de las secciones
)


if seccion == "Paper by topic":
    st.subheader("Paper by topic")
    menu = st.selectbox(
        "Select a Category:",
        set(graph)
    )

    label1 = st.selectbox(
        "Select a Topic:",
        entity(graph, menu)
    )

    st.dataframe(label(graph, menu, label1))


elif seccion == "Authors by category":
    st.subheader("Authors relashionship")

    menu = st.selectbox(
        "Select an entity:",
        set(graph)
    )

    options = ["All"] + label1(graph, menu)
    label = st.selectbox(
        "Select a label:",
        options,
        index=0, key="label1"
    )


    st.markdown("""
        <div style="display: flex; justify-content: left; align-items: left; margin-top: 20px;">
            <div style="margin-right: 20px; display: flex; align-items: right;">
                <div style="background-color: blue; width: 12px; height: 12px; margin-right: 5px;"></div>
                <span>Author</span>
            </div>
            <div style="margin-right: 20px; display: flex; align-items: right;">
                <div style="background-color: green; width: 12px; height: 12px; margin-right: 5px;"></div>
                <span>Category</span>
            </div>
            <div style="display: flex; align-items: right;">
                <div style="background-color: red; width: 12px; height: 12px; margin-right: 5px;"></div>
                <span>Paper</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if label == "All":
        dirc = "graph/" + menu + ".html"
        nt = Network(height="600px", width="100%", notebook=False, directed=False)
        nt.toggle_physics(False)
        st.components.v1.html(open(dirc, "r", encoding="utf-8").read(), height=600)


    else:
        data = authors(graph, menu,label)
        G = authorsGraph(data)
        nt = Network(height="600px", width="100%", notebook=False, directed=False)
        nt.from_nx(G)
        nt.save_graph("label.html")
        st.components.v1.html(open("label.html", "r", encoding="utf-8").read(), height=600)




elif seccion == "Property analysis":
    st.subheader("Property analysis")

    menu = st.selectbox(
        "Select a Property:",
        property(graph)
    )
    st.dataframe(triples(graph, menu))


elif seccion == "Paper analysis":
    st.subheader("Paper analysis")

    paper = st.selectbox(
        "Select a paper:",
        paper(graph)
    )
    chunk = st.selectbox(
        "Select a chunk:",
        chunck(graph,paper)
    )

    st.text("Facts in the chunk")
    st.dataframe(fact(graph, chunk))

    st.write("Chunk Text")

    st.write(chunkText(graph,chunk))



if seccion == "GDS similarity":
    st.subheader("GDS similarity")

    c = st.radio('Similarity Node', ['Author', 'Paper'])

    if c == "Paper":
        paper = st.selectbox(
            "Select a paper:",
            paper(graph)
        )

        # Capturamos el valor actualizado de h
        h = st.radio('Similarity by', ['KeyWord', 'Category'], key="similarity_radio")

        if h == "KeyWord":
            st.dataframe(paperKey(graph, paper))
        elif h == "Category":
            st.dataframe(paperCategory(graph, paper))

    else:
        paper = st.selectbox(
            "Select a paper:",
            paper(graph)
        )
        author = st.selectbox(
            "Select an author:",
            authorsP(graph, paper)
        )

        st.text("Similarity by Key-Paper-Affiliation")
        st.dataframe(authorKey(graph, author))

elif seccion == "Paper search":
    st.subheader("Paper search")

    c = st.radio('Select an element to search:', ['Affiliation', 'Journal', 'Publisher'])

    if c == "Journal":
        menu = st.selectbox(
            "Select a Journal:",
            journal(graph))
        st.dataframe(journal1(graph,menu))



    elif c == "Publisher":
        menu = st.selectbox(
            "Select a Publisher:",
            publisher(graph))
        st.dataframe(publisher1(graph, menu))

    else:
        menu = st.selectbox(
            "Select a Affiliation:",
            affiliation(graph))
        st.dataframe(affiliation1(graph, menu))






