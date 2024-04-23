import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import pandas as pd

# Configuração do banco de dados e modelos
Base = declarative_base()

class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    lotes = relationship('Lote', back_populates='produto')

class Lote(Base):
    __tablename__ = 'lotes'
    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    quantidade = Column(Integer)
    produto = relationship('Produto', back_populates='lotes')
    fases = relationship('FaseDeProducao', back_populates='lote')

class FaseDeProducao(Base):
    __tablename__ = 'fases_de_producao'
    id = Column(Integer, primary_key=True)
    lote_id = Column(Integer, ForeignKey('lotes.id'))
    descricao = Column(String)
    lote = relationship('Lote', back_populates='fases')

engine = create_engine('sqlite:///producao.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Funções de manipulação de dados
def add_produto(nome):
    session = Session()
    novo_produto = Produto(nome=nome)
    session.add(novo_produto)
    session.commit()
    session.close()

def add_lote(produto_id, quantidade):
    session = Session()
    novo_lote = Lote(produto_id=produto_id, quantidade=quantidade)
    session.add(novo_lote)
    session.commit()
    session.close()

def add_fase(lote_id, descricao):
    session = Session()
    nova_fase = FaseDeProducao(lote_id=lote_id, descricao=descricao)
    session.add(nova_fase)
    session.commit()
    session.close()

def get_fases_de_producao():
    session = Session()
    fases = session.query(FaseDeProducao).join(Lote).join(Produto).all()
    data = [
        {"Fase ID": fase.id, "Descrição da Fase": fase.descricao, "Lote ID": fase.lote_id, "Produto": fase.lote.produto.nome, "Quantidade do Lote": fase.lote.quantidade}
        for fase in fases
    ]
    session.close()
    return pd.DataFrame(data)

# Streamlit interface
st.title('Sistema de Gestão de Produção Têxtil')

# Adicionar novo produto
st.subheader('Adicionar novo Produto')
nome_produto = st.text_input('Nome do Produto', key="produto")
if st.button('Adicionar Produto'):
    add_produto(nome_produto)
    st.success('Produto adicionado com sucesso!')

# Adicionar Lote
st.subheader('Adicionar Lote')
session = Session()
produtos = session.query(Produto).all()
produtos_dict = {produto.id: produto.nome for produto in produtos}
produto_selecionado = st.selectbox('Escolha um Produto', options=list(produtos_dict.keys()), format_func=lambda x: produtos_dict[x], key="lote")
quantidade_lote = st.number_input('Quantidade do Lote', min_value=1, value=1, key="quantidade_lote")
if st.button('Adicionar Lote'):
    add_lote(produto_selecionado, quantidade_lote)
    st.success('Lote adicionado com sucesso!')
session.close()

# Adicionar Fase de Produção
st.subheader('Adicionar Fase de Produção')
session = Session()
lotes = session.query(Lote).all()
lotes_dict = {lote.id: f"Lote {lote.id} - Produto: {lote.produto.nome}" for lote in lotes}
lote_selecionado = st.selectbox('Escolha um Lote', options=list(lotes_dict.keys()), format_func=lambda x: lotes_dict[x], key="fase")
descricao_fase = st.text_input('Descrição da Fase', key="descricao_fase")
if st.button('Adicionar Fase de Produção'):
    add_fase(lote_selecionado, descricao_fase)
    st.success('Fase de produção adicionada com sucesso!')
session.close()

# Mostrar Fases de Produção
st.subheader('Visualizar Fases de Produção')
if st.button('Carregar Fases de Produção'):
    df_fases = get_fases_de_producao()
    st.dataframe(df_fases)