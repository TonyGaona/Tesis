import networkx as nx
import pandas as pd
import py2neo
from pyvis.network import Network
from st_aggrid import GridOptionsBuilder
import streamlit as st


def paper(graph):
    query = '''
    MATCH (n:Paper)-[r:hasPart]->(t)
    RETURN DISTINCT n.title as title
    '''
    result = graph.run(query).data()

    return [item['title'] for item in graph.run(query).data()]

def chunck(graph,Paper):
    query = f'''
    MATCH (n:Paper)-[r:hasPart]->(t:Chunk)
    WHERE n.title = '{Paper}'
    RETURN DISTINCT t.identifier as ID
    '''
    result = graph.run(query).data()

    return [item['ID'] for item in graph.run(query).data()]

def set(graph):
    query = '''
    MATCH (n:Fact)-[r]->(t)
    RETURN DISTINCT labels(t) as set
    '''
    result = graph.run(query).data()

    return [label for sublist in result for label in sublist['set']]

def property(graph):
    query = '''
    MATCH (f:Fact)
    WITH f.hasProperty AS PropertyValue, COUNT(*) AS Frequency
    ORDER BY Frequency DESC
    LIMIT 10
    RETURN PropertyValue;
    '''
    result = graph.run(query).data()

    return [item['PropertyValue'] for item in graph.run(query).data()]

def entity(graph, entity):
    query = f'''     
    MATCH (n:Fact)-[r]->(t:{entity})
    WITH t.label AS GroupLabel, COUNT(r) AS RelationshipCount
    ORDER BY RelationshipCount DESC
    LIMIT 10
    RETURN GroupLabel 
    '''
    return [item['GroupLabel'] for item in graph.run(query).data()]

def label(graph, entity1, label1):
    # Formar la consulta con la etiqueta (no puede ser parámetro)
    query = f'''
        MATCH (p:Paper)-[:hasPart]->(c:Chunk)-[:hasPart]->(f:Fact)
        MATCH (f)-[:hasSubject|hasObject]->(a:{entity1} {{label: $label1}})
        RETURN DISTINCT p.title AS title, p.url AS url
        '''
    # Ejecutar la consulta
    return graph.run(query, label1=label1).data()

def authors(graph, entity1,label1):
    # Formar la consulta con la etiqueta (no puede ser parámetro)
    query = f'''
        MATCH (e:{entity1})<-[:hasSubject|:hasObject]-(f:Fact)<-[:hasPart]-(c:Chunk)<-[:hasPart]-(p:Paper)<-[:author]-(a:Author)
        Where "{label1}" = e.label
        RETURN DISTINCT a.name AS Autor, p.identifier AS PaperID, e.label AS Entidad, p.url AS Uri
        '''
    # Ejecutar la consulta
    return graph.run(query).data()



def label1(graph, entity1):
    query = f'''
        MATCH (e:{entity1})<-[:hasSubject|:hasObject]-(f:Fact)<-[:hasPart]-(c:Chunk)<-[:hasPart]-(p:Paper)<-[:author]-(a:Author)
        WITH e.label AS Entidad, p.identifier AS PaperID
        WITH Entidad, COUNT(DISTINCT PaperID) AS Frecuencia
        ORDER BY Frecuencia DESC
        RETURN Entidad
        Limit 10
        '''
    # Ejecutar la consulta
    return [item['Entidad'] for item in graph.run(query).data()]

def authorsGraph(data):
    G = nx.Graph()
    for row in data:
        autor = row["Autor"]
        entidad = row["Entidad"]
        paper = row["PaperID"]
        uri = row["Uri"]

        G.add_node(autor, title=autor, color="blue")
        G.add_node(entidad, title=entidad, color= "green")
        G.add_node(paper, title=f"{paper}<br><a href='{uri}' target='_blank'>PaperLink</a>", color="red")

        G.add_edge(autor, paper, color="gray")
        G.add_edge(paper, entidad, color="gray")
    return G

def triples(graph, property):
    # Formar la consulta con la etiqueta (no puede ser parámetro)
    query = f'''
        MATCH (p:Paper)-[:hasPart]->(c:Chunk)-[:hasPart]->(f:Fact)
        WHERE f.hasProperty = '{property}'
        RETURN p.identifier AS EID, f.hasSubject AS Subject, f.hasProperty as Property, f.hasObject as Object
        ORDER BY Subject DESC
        '''
    # Ejecutar la consulta
    return graph.run(query).data()

def fact(graph, chunk):
    # Formar la consulta con la etiqueta (no puede ser parámetro)
    query = f'''
        MATCH (c:Chunk)-[:hasPart]->(f:Fact)
        WHERE c.identifier = '{chunk}'
        RETURN f.hasSubject AS Subject, f.hasProperty as Property, f.hasObject as Object
        '''
    # Ejecutar la consulta
    return graph.run(query).data()

def chunkText(graph, chunk):
    # Formar la consulta con la etiqueta (no puede ser parámetro)
    query = f'''
        MATCH (c:Chunk)
        WHERE c.identifier = '{chunk}'
        RETURN c.content
        '''
    # Ejecutar la consulta
    return graph.run(query).data()[0]["c.content"]

def graphEliminar(graph):
    query = '''
    CALL gds.graph.list()
    YIELD graphName
    CALL gds.graph.drop(graphName)
    YIELD graphName AS droppedGraph
    RETURN droppedGraph
    '''

    result = graph.run(query)
    result

def graphGDS(graph):
    query = '''
    CALL gds.graph.project(
      'paperGraph',
      ['Paper', 'Fact', 'Chunk', 'Key', 'Technology', 'Method', 'Person', 'Group', 'Algoritm', 'ResearchField', 'Tool','Evaluation'
      ,'DataSet', 'Exprement'],
      {
        keyWords: {
          orientation: 'UNDIRECTED'
        },
        RELATED_TO: {
          orientation: 'UNDIRECTED'
        }


      }
    )
    '''
    graph.run(query)
    query = '''
    CALL gds.graph.project(
      'authorPaper',
      ['Key','Paper', 'Author','Affiliation'],
      {
        author: {
          orientation: 'UNDIRECTED'
        },
        affiliation: {
          orientation: 'UNDIRECTED'
        },
        keyWords: {
          orientation: 'UNDIRECTED'
        }
      }
    )
    '''
    graph.run(query)

def authorsP(graph,paper):
    query = f'''
        MATCH (c:Chunk)<-[:hasPart]-(p:Paper)<-[:author]-(a:Author)
        WHERE p.title = '{paper}'
        WITH a.identifier AS ID, COLLECT(a.name)[0] AS Author
        RETURN ID, Author
        '''
    # Ejecutar la consulta
    return [item['Author'] for item in graph.run(query).data()]



def paperCategory(graph,paper):
    query = f'''
    CALL gds.nodeSimilarity.stream(
      'paperGraph', 
      {{
        relationshipTypes: ['RELATED_TO']
      }}
    )
    YIELD node1, node2, similarity
    WITH gds.util.asNode(node1) AS n1, gds.util.asNode(node2) AS n2, similarity
    WHERE n1.title = "{paper}"
    RETURN n2.title AS Paper, similarity AS Similarity
    ORDER BY Similarity DESC, Paper
    '''

    return graph.run(query).data()

def paperKey(graph,paper):
    query = f'''
    MATCH (p1:Paper)-[r:SIMILAR_BY_KEY]->(p2:Paper)
    WHERE p1.title = "{paper}"
    RETURN p2.title AS Paper, r.similarity AS Similarity
    ORDER BY Similarity DESC 
    '''

    return graph.run(query).data()

def authorKey(graph,name):
    query = f'''
    MATCH (p1:Author)-[r:AUTHOR_SIMILARITY]->(p2:Author)
    WHERE p1.name = "{name}"
    AND p1.identifier <> p2.identifier
    WITH p2.identifier AS AuthorID, MAX(r.similarity) AS MaxSimilarity
    MATCH (a:Author) WHERE a.identifier = AuthorID
    WITH AuthorID, COLLECT(a.name)[0] AS AuthorName, MaxSimilarity
    RETURN AuthorID, AuthorName, MaxSimilarity AS Similarity
    ORDER BY Similarity DESC
    '''
    return graph.run(query).data()

def journal(graph):
    query = f'''
        MATCH (n:Journal)
        RETURN DISTINCT n.title as title
        '''
    return [item['title'] for item in graph.run(query).data()]

def publisher(graph):
    query = f'''
        MATCH (n:Publisher)
        RETURN DISTINCT n.name as name
        '''
    return [item['name'] for item in graph.run(query).data()]

def affiliation(graph):
    query = f'''
        MATCH (n:Affiliation)
        RETURN DISTINCT n.name as name
        '''
    return [item['name'] for item in graph.run(query).data()]

def journal1(graph,label):
    query = f'''
        MATCH (p1:Journal)<-[r:sdPublisher]-(p2:Paper)
        where p1.title = "{label}"
        RETURN DISTINCT p2.identifier as EID, p2.title as Title, p2.url as Url
        '''
    return graph.run(query).data()

def publisher1(graph,label):
    query = f'''
        MATCH (p1:Publisher)<-[r:publisher]-(p2:Paper)
        where p1.name = "{label}"
        RETURN DISTINCT p2.identifier as EID, p2.title as Title, p2.url as Url
        '''
    return graph.run(query).data()

def affiliation1(graph,label):
    query = f'''
        MATCH (p1:Affiliation)<-[r:affiliation]-(p2:Author)<-[r1:creator]-(p3:Paper)
        where p1.name = "{label}"
        RETURN DISTINCT p3.identifier as EID, p3.title as Title, p3.url as Url
        '''
    return graph.run(query).data()